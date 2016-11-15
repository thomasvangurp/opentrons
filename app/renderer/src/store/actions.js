import Vue from 'vue'
import * as types from './mutation-types'
import OpenTrons from '../rest_api_wrapper'
import {addHrefs, processTasks} from '../util'


const actions = {
  connect_robot ({ commit }, port) {
    const payload = {is_connected: true, 'port': port}
    OpenTrons.connect(port).then((was_successful) => {
      if (was_successful) {
        commit(types.UPDATE_ROBOT_CONNECTION, payload)
        if (window.confirm("Successfully Connected. Do you want to home now?")) {
          OpenTrons.home('all')
        }
        OpenTrons.getVersions().then((result) => {
          let versions = result
          commit(types.UPDATE_ROBOT_VERSIONS, {versions})
        })
      }
    })
  },
  disconnect_robot ({ commit }) {
    OpenTrons.disconnect().then((was_successful) => {
      if (was_successful) {
        commit(types.UPDATE_ROBOT_CONNECTION, {'is_connected': false, 'port': null})
      }
    })
  },
  uploadProtocol ({commit}, formData) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    commit(types.UPLOADING, {'uploading': true})
    OpenTrons.uploadProtocol(formData).then((result) => {
      let tasks
      if (result.success) {
        tasks = processTasks(result, commit)
      } else {
        tasks = []
      }
      commit(types.UPDATE_WARNINGS, {warning: result.warnings})
      commit(types.UPDATE_ERROR, {errors: result.errors})
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
      commit(types.UPLOADING, {'uploading': false})
      commit(types.UPDATE_TASK_LIST, {'tasks': tasks})
    })
  },
  loadProtocol ({commit}) {
    OpenTrons.loadProtocol().then((result) => {
      if (result.success) {
        let tasks = processTasks(result, commit)
        commit(types.UPDATE_TASK_LIST, {tasks})
      } else {
        commit(types.UPDATE_TASK_LIST, {tasks: []})
      }
    })
  },
  selectIncrement ({commit}, data) {
    commit(types.UPDATE_INCREMENT, { 'current_increment': data.inc })
  },
  selectIncrementPlunger ({commit}, data) {
    commit(types.UPDATE_INCREMENT_PLUNGER, { 'current_increment_plunger': data.inc })
  },
  jog ({commit}, coords) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.jog(coords).then((result) => {
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
    })
  },
  jogToSlot ({commit}, data) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.jogToSlot(data).then(() => {
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
    })
  },
  calibrate ({commit}, data) {
    let type = "plunger"
    if (data.slot) { type = "placeable"}
    OpenTrons.calibrate(data, type).then((tasks) => {
      if (tasks) {
        commit('UPDATE_TASK_LIST', {'tasks': tasks})
      }
    })
  },
  moveToPlaceable({commit}, data) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    Vue.http
    .post('http://localhost:31950/move_to_container', JSON.stringify(data), {emulateJSON: true})
    .then((response) => {
       commit(types.UPDATE_ROBOT_STATE, {'busy': false})
       console.log('success',response)
    }, (response) => {
       commit(types.UPDATE_ROBOT_STATE, {'busy': true})
       console.log('failed', response)
    })
  },
  runProtocol({ commit }) {
    commit(types.UPDATE_RUNNING, {'running': true})
    commit(types.RESET_RUN_LOG)
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.runProtocol()
  },
  pauseProtocol({ commit }) {
    OpenTrons.pauseProtocol().then((was_successful) => {
      console.log(was_successful)
      if (was_successful) {
        commit(types.UPDATE_PAUSED, was_successful)
      }
    })
  },
  resumeProtocol({ commit }) {
    OpenTrons.resumeProtocol().then((was_successful) => {
      console.log(was_successful)
      if (was_successful) {
        commit(types.UPDATE_PAUSED, !was_successful)
      }
    })
  },
  cancelProtocol({ commit }) {
    OpenTrons.cancelProtocol()
  },
  moveToPosition ({commit}, data) {
    let type = "plunger"
    if (data.slot) { type = "placeable" }
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.moveToPosition(data, type).then(() => {
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
    })
  },
  pickUpTip ({commit}, data) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.pickUpTip(data).then(() => {
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
    })
  },
  dropTip ({commit}, data) {
    OpenTrons.dropTip(data)
  },
  aspirate ({commit}, data) {
    OpenTrons.aspirate(data)
  },
  dispense ({commit}, data) {
    OpenTrons.dispense(data)
  },
  maxVolume({commit}, data) {
    OpenTrons.maxVolume(data).then((result) => {
      if (result) {
        OpenTrons.loadProtocol().then((result) => {
          if (result.success) {
            let tasks = processTasks(result, commit)
            commit(types.UPDATE_TASK_LIST, {tasks})
          } else {
            commit(types.UPDATE_TASK_LIST, {tasks: []})
          }
        })
      }
    })
  },
  home ({commit}, data) {
    commit(types.UPDATE_ROBOT_STATE, {'busy': true})
    OpenTrons.home(data.axis).then(() => {
      commit(types.UPDATE_ROBOT_STATE, {'busy': false})
    })
  }
}

export default {
  actions
}
