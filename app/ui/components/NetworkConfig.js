import React, {Component} from 'react'
import classnames from 'classnames'
import Button from './Button'
import styles from './NetworkConfig.css'

export default class NetworkConfig extends Component {
  constructor (props) {
    super(props)
    this.state = {
      hostname: this.props.hostname,
      network: '',
      password: ''
    }
  }
  render () {
    return (
      <div className={styles.settings}>
        <label className={styles.label}>
          Network
        </label>
        <input
          type='text'
          value={this.state.network}
          onChange={event => this.setState({network: event.target.value})}
          className={styles.input}
        />
        <label className={styles.label}>
          Password
        </label>
        <input
          type='password'
          value={this.state.password}
          onChange={event => this.setState({password: event.target.value})}
          className={styles.input}
        />
        <Button
          onClick={() => console.log('join')}
          style={classnames('btn_dark', styles.btn_join)}
        >
          Join Network
        </Button>
      </div>
    )
  }
}
