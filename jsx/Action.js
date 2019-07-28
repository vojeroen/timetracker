import React, {Component} from "react";
import {Button, List, Segment} from "semantic-ui-react";
import axios from "axios";
import HOST from "./Constants"

class ActionButton extends Component {
    constructor(props) {
        super(props);
        this.state = {
            update: true
        };
    }

    render() {
        let color = null;
        let icon = "play";
        let callback = (event, data) => this.props.onActivate(this.props.id);

        if (this.props.loading) {
            icon = "sync";
            callback = (event, data) => this.props.onActivate(this.props.id);
        } else if (this.props.error) {
            color = "red";
            icon = "close";
            callback = (event, data) => this.props.onActivate(this.props.id);
        } else if (this.props.active) {
            color = "green";
            icon = "pause";
            callback = (event, data) => this.props.onDeactivate(this.props.id);
        }

        let show_update = null;

        if (this.state.update) {
            show_update = <Button color={color} content={"Update"}/>
        }

        return <List.Item>
            <Button fluid icon={icon} color={color} labelPosition={"left"}
                    content={this.props.name} onClick={callback}/>
        </List.Item>
    }
}

export class ActionView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            actions: [],
            active: null,
            error: [],
            loading: [],
        };
        this.setInactive = this.setInactive.bind(this);
        this.setActive = this.setActive.bind(this);
    }

    componentDidMount() {
        axios.get(HOST + '/api/action')
            .then((response) => {
                this.setState({actions: response.data});
            });
        axios.get(HOST + '/api/registration', {params: {latest: true}})
            .then((response) => {
                if (response.data.length > 0) {
                    if (response.data[0].timestamp_end === null) {
                        this.setState({active: response.data[0].action_id})
                    }
                }
            })
    }

    removeError(id) {
        this.setState((prevState) => {
            let newError = prevState.error;
            let idx = newError.indexOf(id);
            if (idx > -1) {
                newError.splice(idx, 1);
            }
            return {
                error: newError
            }
        })
    }

    postAction(id, active) {
        this.setState((prevState) => {
            let newLoading = prevState.loading;
            let idx = newLoading.indexOf(id);
            if (idx === -1) {
                newLoading = [...newLoading, id]
            }
            return {loading: newLoading}
        });
        axios.post(HOST + '/api/registration', {id: id, active: active})
            .then((response) => {
                this.setState((prevState) => {
                    let newActive = null;
                    if (active === true) {
                        newActive = id;
                    }
                    let newLoading = prevState.loading;
                    let idx = newLoading.indexOf(id);
                    if (idx > -1) {
                        newLoading.splice(idx, 1);
                    }
                    return {
                        active: newActive,
                        loading: newLoading
                    }
                })
            }).catch((response) => {
            this.setState((prevState) => {
                let newLoading = prevState.loading;
                let idx = newLoading.indexOf(id);
                if (idx > -1) {
                    newLoading.splice(idx, 1);
                }
                let newError = prevState.error;
                idx = newError.indexOf(id);
                if (idx === -1) {
                    newError = [...newError, id];
                }
                setTimeout(() => {
                    this.removeError(id)
                }, 1500);
                return {
                    error: newError,
                    loading: newLoading
                }
            })
        })
        ;
    }

    setInactive(id) {
        this.postAction(id, false)
    }

    setActive(id) {
        this.postAction(id, true);
    }

    render() {
        return <Segment basic>
            <List relaxed>
                {this.state.actions.map((action) =>
                    <ActionButton key={action.id}
                                  {...action}
                                  active={action.id === this.state.active}
                                  error={this.state.error.indexOf(action.id) > -1}
                                  loading={this.state.loading.indexOf(action.id) > -1}
                                  onActivate={this.setActive}
                                  onDeactivate={this.setInactive}
                    />
                )}
            </List>
        </Segment>;
    }
}