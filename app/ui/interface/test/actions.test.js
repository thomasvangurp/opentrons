// interface actions test

import {actions, actionTypes} from '../'

describe('interface actions', () => {
  test('toggle nav panel', () => {
    const expected = {type: actionTypes.TOGGLE_NAV_PANEL}

    expect(actions.toggleNavPanel()).toEqual(expected)
  })

  test('set current nav panel', () => {
    const expected = {type: actionTypes.SET_CURRENT_NAV_PANEL, payload: {panel: 'upload'}}

    expect(actions.setCurrentNavPanel('upload')).toEqual(expected)
  })

  test('set settings panel open', () => {
    const expected = {type: actionTypes.TOGGLE_SETTINGS_PANEL}
    expect(actions.toggleSettingsPanel()).toEqual(expected)
  })
})
