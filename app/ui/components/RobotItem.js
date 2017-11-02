import React from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

import Button from './Button'
import NetworkSettings from '../containers/NetworkSettings'
import {ControlledUSB, AvailableUSB} from './icons'
import styles from './ConnectPanel.css'

RobotItem.propTypes = {
  hostname: PropTypes.string.isRequired,
  isConnected: PropTypes.bool.isRequired,
  onSettingsClick: PropTypes.func,
  onConnectClick: PropTypes.func,
  onDisconnectClick: PropTypes.func
}

export default function RobotItem (props) {
  const {
    hostname,
    isConnected,
    onConnectClick,
    onDisconnectClick,
    onSettingsClick,
    settingsOpen
  } = props
  let connectionToggle
  let connectionStatus
  const networkPanel = settingsOpen
  ? <NetworkSettings hostname={hostname} />
  : null

  if (isConnected) {
    connectionStatus = <ControlledUSB className={styles.connection_type} />
    connectionToggle = (
      <span>
        <Button
          onClick={onSettingsClick}
          style={classnames('btn_dark', styles.btn_connect)}
        >
          Settings
        </Button>
        <Button
          onClick={onDisconnectClick}
          style={classnames('btn_dark', styles.btn_connect)}
        >
          Release Control
        </Button>
      </span>
    )
  } else {
    connectionStatus = <AvailableUSB className={styles.connection_type} />
    connectionToggle = (
      <Button
        onClick={onConnectClick}
        style={classnames('btn_dark', styles.btn_connect)}
      >
        Take Control
      </Button>
    )
  }

  return (
    <li>
      <div>
        {connectionStatus}
        <div className={styles.connection_info}>
          <span className={styles.connection_name}>{hostname}</span>
          <span className={styles.connection_btn}>{connectionToggle}</span>
        </div>
      </div>
      {networkPanel}
    </li>
  )
}
