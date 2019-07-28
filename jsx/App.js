import React, {Component} from 'react';
import {HashRouter as Router, Link, Route} from "react-router-dom";
import {Container, Menu, Segment} from 'semantic-ui-react';
import {ActionView} from "./Action";
import {StatsView} from "./Stats";

class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <Router>
            <Container>
                <Segment basic>
                    <Menu>
                        <Menu.Item as={Link} to="/actions/">Actions</Menu.Item>
                        <Menu.Item as={Link} to="/stats/">Stats</Menu.Item>
                    </Menu>
                </Segment>
                <Route exact path="/" component={ActionView}/>
                <Route path="/actions/" component={ActionView}/>
                <Route path="/stats/" component={StatsView}/>
            </Container>
        </Router>;
    }
}

export default App;
