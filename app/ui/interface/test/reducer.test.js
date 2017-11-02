// interface reducer test

import {reducer, actionTypes} from '../'
import {
  actionTypes as robotActionTypes
} from '../../robot'

describe('interface reducer', () => {
  test('initial state', () => {
    const state = reducer(undefined, {})

    expect(state).toEqual({
      isNavPanelOpen: false,
      currentNavPanelTask: '',
      isSettingsPanelOpen: false
    })
  })

  test('handles toggleNavPanel', () => {
    const action = {type: actionTypes.TOGGLE_NAV_PANEL}

    let state = {isNavPanelOpen: false}
    expect(reducer(state, action)).toEqual({isNavPanelOpen: true})

    state = {isNavPanelOpen: true}
    expect(reducer(state, action)).toEqual({isNavPanelOpen: false})
  })

  test('handles setCurrentNavPanel with nav panel closed', () => {
    const state = {currentNavPanelTask: 'upload', isNavPanelOpen: false}
    const panel = 'connect'
    const action = {type: actionTypes.SET_CURRENT_NAV_PANEL, payload: {panel}}

    expect(reducer(state, action)).toEqual({
      currentNavPanelTask: 'connect',
      isNavPanelOpen: true
    })
  })

  test('handles toggleSettingsPanel on settings button click', () => {
    const state = {isSettingsPanelOpen: false}
    const action = {type: actionTypes.TOGGLE_SETTINGS_PANEL}

    expect(reducer(state, action)).toEqual({
      isSettingsPanelOpen: true
    })
  })

  test('handles toggleSettingsPanel on robot disconnect', () => {
    const state = {isSettingsPanelOpen: true}
    const action = {type: robotActionTypes.DISCONNECT}
    expect(reducer(state, action)).toEqual({
      isSettingsPanelOpen: false
    })
  })
})
