// user interface state module
import {makeActionName} from '../util'
import {actionTypes as robotActionTypes} from '../robot'

export const NAME = 'interface'

const makeInterfaceActionName = (action) => makeActionName(NAME, action)
const getModuleState = (state) => state[NAME]

const INITIAL_STATE = {
  isNavPanelOpen: false,
  currentNavPanelTask: '',
  isSettingsPanelOpen: false
}

export const selectors = {
  getIsNavPanelOpen (allState) {
    return getModuleState(allState).isNavPanelOpen
  },
  getCurrentNavPanelTask (allState) {
    return getModuleState(allState).currentNavPanelTask
  },
  getIsSettingsPanelOpen (allState) {
    return getModuleState(allState).isSettingsPanelOpen
  }
}

export const actionTypes = {
  TOGGLE_NAV_PANEL: makeInterfaceActionName('TOGGLE_NAV_PANEL'),
  SET_CURRENT_NAV_PANEL: makeInterfaceActionName('SET_CURRENT_NAV_PANEL'),
  TOGGLE_SETTINGS_PANEL: makeInterfaceActionName('TOGGLE_SETTINGS_PANEL')
}

export const actions = {
  toggleNavPanel () {
    return {
      type: actionTypes.TOGGLE_NAV_PANEL
    }
  },
  setCurrentNavPanel (panel) {
    return {type: actionTypes.SET_CURRENT_NAV_PANEL, payload: {panel}}
  },
  toggleSettingsPanel () {
    return {type: actionTypes.TOGGLE_SETTINGS_PANEL}
  }
}

export function reducer (state = INITIAL_STATE, action) {
  const {type, payload} = action

  switch (type) {
    case actionTypes.TOGGLE_NAV_PANEL:
      return {...state, isNavPanelOpen: !state.isNavPanelOpen}

    case actionTypes.SET_CURRENT_NAV_PANEL:
      return {
        ...state,
        currentNavPanelTask: payload.panel,
        isNavPanelOpen: (
          !state.isNavPanelOpen ||
          payload.panel !== state.currentNavPanelTask
        )
      }
    case actionTypes.TOGGLE_SETTINGS_PANEL:
      return {...state, isSettingsPanelOpen: !state.isSettingsPanelOpen}

    case robotActionTypes.DISCONNECT:
      return {...state, isSettingsPanelOpen: false}
  }
  return state
}
