import {connect} from 'react-redux'

import RobotItem from '../components/RobotItem'

import {
  actions as robotActions
} from '../robot'

import {
  actions as interfaceActions,
  selectors as interfaceSelectors
} from '../interface'

const mapStateToProps = (state, ownProps) => {
  const settingsOpen = interfaceSelectors.getIsSettingsPanelOpen(state)
  const isConnected = ownProps.isConnected
  return {
    ...ownProps,
    settingsOpen: (settingsOpen && isConnected)
  }
}

const mapDispatchToProps = (dispatch, ownProps) => {
  // only allow disconnect if connected and vice versa
  if (ownProps.isConnected) {
    return {
      onDisconnectClick: () => dispatch(robotActions.disconnect()),
      onSettingsClick: () => dispatch(interfaceActions.toggleSettingsPanel())
    }
  }

  return {
    onConnectClick: () => dispatch(robotActions.connect(ownProps.hostname))
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(RobotItem)
