// RPC client tests
import EventEmitter from 'events'
import portfinder from 'portfinder'
import WS from 'ws'
// import log from 'winston'

import Client from '../../rpc/client'
import {
  statuses,
  RESULT,
  ACK,
  NACK,
  NOTIFICATION,
  CONTROL_MESSAGE
} from '../../rpc/message-types'

// log.level = 'debug'

const {SUCCESS, FAILURE} = statuses

const EX_REMOTE = {i: 4, t: 5, v: {foo: 'bar'}}
const EX_REMOTE_TYPE = {i: 5, t: 3, v: {be_a_robot: {}, be_a_person: {}}}
const EX_CONTROL_MESSAGE = {
  $: {type: CONTROL_MESSAGE},
  root: EX_REMOTE,
  type: EX_REMOTE_TYPE
}

const EX_ROOT_TYPE = {i: 5, t: 3, v: {be_a_robot: {}, be_a_person: {}}}

const makeAckResponse = (token) => ({$: {type: ACK, token}})
const makeNackResponse = (token, reason) => ({$: {type: NACK, token}, reason})
const makeCallResponse = (token, status, data) => ({
  $: {type: RESULT, token, status},
  data
})

describe('rpc client', () => {
  let url
  let wss
  let listeners

  function addListener (target, event, handler) {
    listeners.push({target, event, handler})
    target.on(event, handler)
  }

  function removeListener (listener) {
    listener.target.removeListener(listener.event, listener.handler)
  }

  class JsonWs extends EventEmitter {
    constructor (ws) {
      super()
      this._ws = ws

      addListener(ws, 'message', (m) => this.emit('message', JSON.parse(m)))
      addListener(ws, 'close', () => this.emit('close'))
    }

    send (message) {
      this._ws.send(JSON.stringify(message))
    }

    get readyState () {
      return this._ws.readyState
    }
  }

  beforeAll((done) => portfinder.getPort((error, port) => {
    if (error) return done(error)
    if (!global.WebSocket) global.WebSocket = WS

    url = `ws://127.0.0.1:${port}`
    wss = new WS.Server({port})
    wss.once('listening', done)
  }))

  afterAll((done) => {
    if (global.WebSocket === WS) delete global.WebSocket
    wss.close(done)
  })

  beforeEach(() => {
    listeners = []
  })

  afterEach(() => {
    listeners.forEach(removeListener)
  })

  test('rejects if control message never comes', () => {
    const result = Client(url)

    return expect(result).rejects.toMatchObject({
      message: expect.stringMatching(/timeout/i)
    })
  })

  test('connects to ws server and resolves when control is received', () => {
    addListener(wss, 'connection', (ws) => new JsonWs(ws).send(EX_CONTROL_MESSAGE))

    return expect(Client(url)).resolves.toBeDefined()
  })

  test('resolves with a proxy for the remote object', () => {
    addListener(wss, 'connection', (ws) => new JsonWs(ws).send(EX_CONTROL_MESSAGE))

    return expect(Client(url)).resolves.toMatchObject({
      remote: {
        foo: 'bar',
        be_a_robot: expect.any(Function),
        be_a_person: expect.any(Function)
      }
    })
  })

  describe('with good connection', () => {
    let client
    let ws

    beforeEach(() => {
      addListener(wss, 'connection', (websocket) => {
        ws = new JsonWs(websocket)
        ws.send(EX_CONTROL_MESSAGE)
      })

      return Client(url).then((c) => (client = c))
    })

    test('calls a method of a remote object', (done) => {
      addListener(ws, 'message', (message) => {
        expect(message).toEqual({
          $: {
            token: expect.anything()
          },
          id: EX_REMOTE.i,
          name: 'be_a_person',
          args: ['foo', 'bar']
        })

        done()
      })

      client.remote.be_a_person('foo', 'bar')
    })

    test('rejects the result of a failed method call', () => {
      const exResponse = (token) => makeCallResponse(token, FAILURE, 'ahhh')

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(exResponse(token)), 5)
      })

      const result = client.remote.be_a_robot(1, 2)

      return expect(result).rejects.toMatchObject({
        message: expect.stringMatching(/ahhh/)
      })
    })

    test("rejects the result of a nack'd method call", () => {
      addListener(ws, 'message', (message) => {
        const token = message.$.token
        ws.send(makeNackResponse(token, 'You done messed up'))
      })

      const result = client.remote.be_a_person('Tim')

      return expect(result).rejects.toMatchObject({
        message: expect.stringMatching(/NACK.+You done messed up/)
      })
    })

    test('resolves a null result of method call', () => {
      addListener(ws, 'message', (message) => {
        const token = message.$.token

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, null)), 5)
      })

      return client.remote.be_a_person()
        .then((result) => expect(result).toEqual(null))
    })

    test('resolves a primitive result of method call', () => {
      const VALUE = 'foobar'

      addListener(ws, 'message', (message) => {
        const token = message.$.token

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, VALUE)), 5)
      })

      return client.remote.be_a_robot()
        .then((result) => expect(result).toEqual(VALUE))
    })

    test('deserializes an array of primitives or null values', () => {
      const VALUE = [1, null, 'foo']

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, VALUE)), 5)
      })

      return client.remote.be_a_person()
        .then((result) => expect(result).toEqual(VALUE))
    })

    test('resolves an object result of a known type', () => {
      const exResponse = (token) => makeCallResponse(
        token,
        SUCCESS,
        {i: 1, t: EX_ROOT_TYPE.i, v: {baz: 'qux'}}
      )

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(exResponse(token)), 5)
      })

      const result = client.remote.be_a_robot()

      return expect(result).resolves.toMatchObject({
        baz: 'qux',
        be_a_robot: expect.any(Function),
        be_a_person: expect.any(Function)
      })
    })

    test('resolves an object of unknown type by getting the type', () => {
      const ID = 256
      const TYPE_ID = 42
      const instanceResponse = (token) => makeCallResponse(token, SUCCESS, {
        i: ID,
        t: TYPE_ID,
        v: {a: 'bc'}
      })

      const typeResponse = (token) => makeCallResponse(token, SUCCESS, {
        i: TYPE_ID,
        t: 3,
        v: {hello_world: {}}
      })

      let messageCount = 0
      let getTypeCall
      addListener(ws, 'message', (message) => {
        const token = message.$.token

        if (messageCount === 0) {
          // first message: should call be_a_person on remote root
          // checked in previous test so no assertions here
          setTimeout(() => ws.send(makeAckResponse(token)), 1)
          setTimeout(() => ws.send(instanceResponse(token)), 5)
        } else if (messageCount === 1) {
          // second message should be a get_object_by_id for the type
          getTypeCall = message
          // return an ack, then return the type object
          setTimeout(() => ws.send(makeAckResponse(token)), 1)
          setTimeout(() => ws.send(typeResponse(token)), 5)
        }

        messageCount++
      })

      return client.remote.be_a_person()
        .then((result) => {
          expect(getTypeCall).toMatchObject({
            id: null,
            name: 'get_object_by_id',
            args: [TYPE_ID]
          })

          expect(result).toEqual({
            a: 'bc',
            hello_world: expect.any(Function)
          })
        })
    })

    test('creates remote objects for all non-primitive children', () => {
      const EX_DEEP_TYPE_3 = {i: 11, t: 3, v: {thing_3: {}}}
      const EX_DEEP_INSTANCE_3 = {i: 10, t: 11, v: {quux: 'quux'}}

      const EX_DEEP_TYPE_2 = {i: 13, t: 3, v: {thing_2: {}}}
      const EX_DEEP_INSTANCE_2 = {
        i: 12,
        t: 13,
        v: {baz: 'baz', instance_3: EX_DEEP_INSTANCE_3}
      }

      const EX_DEEP_TYPE_1 = {i: 15, t: 3, v: {thing_1: {}}}
      const EX_DEEP_INSTANCE_1 = {i: 14, t: 15, v: {bar: 'bar'}}

      const EX_DEEP_TYPE_0 = {i: 17, t: 3, v: {thing_0: {}}}
      const EX_DEEP_INSTANCE_0 = {
        i: 16,
        t: 17,
        v: {foo: 'foo', instance_1: EX_DEEP_INSTANCE_1, instance_2: EX_DEEP_INSTANCE_2}
      }

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        const requestedId = message.args[0]
        let response

        // will be a bunch of control.get_object_by_id calls
        // don't care about recursion order as long as result is correct
        if (requestedId === EX_DEEP_TYPE_3.i) {
          response = EX_DEEP_TYPE_3
        } else if (requestedId === EX_DEEP_TYPE_2.i) {
          response = EX_DEEP_TYPE_2
        } else if (requestedId === EX_DEEP_TYPE_1.i) {
          response = EX_DEEP_TYPE_1
        } else if (requestedId === EX_DEEP_TYPE_0.i) {
          response = EX_DEEP_TYPE_0
        } else {
          // else it wasn't a system get_object_by_id call
          response = EX_DEEP_INSTANCE_0
        }

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, response)), 5)
      })

      const result = client.remote.be_a_person()

      return expect(result).resolves.toEqual({
        thing_0: expect.any(Function),
        foo: 'foo',
        instance_1: {
          thing_1: expect.any(Function),
          bar: 'bar'
        },
        instance_2: {
          thing_2: expect.any(Function),
          baz: 'baz',
          instance_3: {
            thing_3: expect.any(Function),
            quux: 'quux'
          }
        }
      })
    })

    test('deserializes remote objects with nested circular references', () => {
      const CIRCULAR_TYPE = {i: 21, t: 3, v: {circle: {}}}
      const CIRCULAR_INSTANCE = {
        i: 20,
        t: 21,
        v: {foo: 'foo', self: {i: 20, t: 21, v: null}}
      }

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        const requestedId = message.args[0]
        let response

        if (requestedId === CIRCULAR_TYPE.i) {
          response = CIRCULAR_TYPE
        } else {
          response = CIRCULAR_INSTANCE
        }

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, response)), 5)
      })

      return client.remote.be_a_robot()
        .then((remote) => expect(remote.self).toBe(remote))
    })

    test('deserializes remote object with sibling circular refs', () => {
      const TYPE = {i: 30, t: 3, v: {}}
      const CHILD_INSTANCE = {i: 31, t: 30, v: {foo: 'foo'}}
      const CIRCULAR_CHILD_INSTANCE = {i: 31, t: 30, v: null}
      const PARENT_INSTANCE = {
        i: 32,
        t: 30,
        v: {circular: CIRCULAR_CHILD_INSTANCE, child: CHILD_INSTANCE}
      }

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        const requestedId = message.args[0]
        let response

        if (requestedId === TYPE.i) {
          response = TYPE
        } else {
          response = PARENT_INSTANCE
        }

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, response)), 5)
      })

      return client.remote.be_a_robot()
        .then((remote) => {
          expect(remote.circular).toBe(remote.child)
          expect(remote.child).toEqual({foo: 'foo'})
        })
    })

    test('deserializes remote object with deep matching refs', () => {
      const TYPE = {i: 30, t: 3, v: {}}
      const CHILD = {i: 31, t: 30, v: {foo: 'foo'}}
      const ALSO_CHILD = {i: 31, t: 30, v: null}
      const PARENT_1 = {i: 32, t: 30, v: {c: ALSO_CHILD}}
      const PARENT_2 = {i: 33, t: 30, v: {c: CHILD}}
      const SUPERPARENT = {i: 34, t: 30, v: {a: PARENT_1, b: PARENT_2}}

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        const requestedId = message.args[0]
        let response

        if (requestedId === TYPE.i) {
          response = TYPE
        } else {
          response = SUPERPARENT
        }

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, response)), 5)
      })

      return client.remote.be_a_person()
        .then((remote) => {
          expect(remote.a.c).toBe(remote.b.c)
          expect(remote.a.c).toEqual({foo: 'foo'})
        })
    })

    test('deserializes object with null, primitive, and array children', () => {
      const TYPE = {i: 30, t: 3, v: {}}
      const INSTANCE = {i: 32, t: 30, v: {foo: 'bar', baz: null, qux: [1, 2]}}

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        const requestedId = message.args[0]
        let response

        if (requestedId === TYPE.i) {
          response = TYPE
        } else {
          response = INSTANCE
        }

        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, response)), 5)
      })

      return client.remote.be_a_robot()
        .then((remote) => expect(remote).toEqual({
          foo: 'bar',
          baz: null,
          qux: [1, 2]
        }))
    })

    test('emits notification events', (done) => {
      const TYPE = {i: 30, t: 3, v: {}}
      const INSTANCE = {i: 32, t: 30, v: {foo: 'bar', baz: 'quux'}}
      const notification = {$: {type: NOTIFICATION}, data: INSTANCE}

      addListener(ws, 'message', (message) => {
        const token = message.$.token
        setTimeout(() => ws.send(makeAckResponse(token)), 1)
        setTimeout(() => ws.send(makeCallResponse(token, SUCCESS, TYPE)), 5)
      })

      setTimeout(() => ws.send(notification), 5)

      addListener(client, 'notification', (message) => {
        expect(message).toEqual({foo: 'bar', baz: 'quux'})
        done()
      })
    })

    test('closes the socket', () => {
      return client.close()
        .then(() => expect(
          ws.readyState === global.WebSocket.CLOSING ||
          ws.readyState === global.WebSocket.CLOSED
        ).toBe(true))
    })

    test('client.close resolves if the socket is already closed', () => {
      return client.close()
        .then(() => client.close())
        .then(() => expect(
          ws.readyState === global.WebSocket.CLOSING ||
          ws.readyState === global.WebSocket.CLOSED
        ).toBe(true))
    })
  })
})