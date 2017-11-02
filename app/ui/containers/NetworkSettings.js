import {connect} from 'react-redux'

import {
  // selectors as robotSelectors,
  // actions as robotActions
} from '../robot'

import NetworkConfig from '../components/NetworkConfig'

const mapStateToProps = (state, ownProps) => ({
  network: ownProps.network,
  password: ownProps.password
})

const mapDispatchToProps = (dispatch) => ({
  // onJoinNetwork: () => dispatch(robotActions.joinNetwork())
})

export default connect(mapStateToProps, mapDispatchToProps)(NetworkConfig)
