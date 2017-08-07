from functools import wraps
import inspect
# from opentrons.containers import Well

def traceable(*args):
    def _traceable(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            broker = EventBroker.get_instance()

            # Create the initial dictionary with args that have defaults
            args_dict = {}

            if inspect.getargspec(f).defaults:
                args_dict = dict(
                    zip(
                        reversed(inspect.getargspec(f).args),
                        reversed(inspect.getargspec(f).defaults)))

            # Update / insert values for positional args
            args_dict.update(dict(zip(inspect.getargspec(f).args, args)))

            # Update it with values for named args
            args_dict.update(kwargs)

            # args_dict = {k: str(v) for k, v in args_dict.items()}

            broker.notify({
                'name': name,
                'function': f.__qualname__,
                'arguments': args_dict,
                'result': res
            })
            return res
        return decorated

    if len(args) == 1 and callable(args[0]):
        # No event name override in the args:
        # @traceable
        # def foo()
        f, = args
        name = f.__qualname__
        return _traceable(f)
    else:
        # Event name is overriden:
        # @traceable('event-foo')
        # def foo()
        name, = args
        return _traceable

def objects_from_args(arguments):
    print(arguments)

def parse_event(command_info):
    '''
    This takes in the command_info from an event and
    returns an iterable of objects that should receive the data,
    an event_name and a cleaned dict of the data to send

    :param command_info:
    :return objects to dispatch to, name of event, and event_info to send:
    '''
    objects = []
    name, event_info = None, None

    name = command_info['name']
    args = command_info.get('arguments', None)

    print("COMMAND: {}".format(command_info))

    if name == 'dispense': #dispense events should only occur in a well
        well, pipette = args['well'], args['self']
        liquids = pipette._state['liquids']
        objects.extend([pipette, well])
        event_info = {'volume': args['volume'],
                      'liquids': liquids}

    elif name == 'aspirate': #dispense events should only occur from a well
        well, pipette = args['well'], args['self']
        volume = args['volume']
        liquids = well._state['liquids']
        objects.extend([pipette, well])
        event_info = {'volume': volume,
                      'liquids': liquids}

    return objects, name, event_info

class EventBroker(object):
    _instance = None

    def __init__(self):
        self._tracked_objects = {}

    def add(self, object, handler):
        self._tracked_objects.update({id(object): handler})

    def remove(self, f):
        self._tracked_objects.pop(id(f))

    def notify(self, command_info):
        '''
        Passes information about tracked operations
         to the state handlers of the objects that they
         affect
        '''
        objects, event_name, event_info \
            = parse_event(command_info)
        if objects:
            [self._tracked_objects[id(object)](event_name, event_info)
             for object in objects]

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = EventBroker()
        return cls._instance
