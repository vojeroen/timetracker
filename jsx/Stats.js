import React, {Component} from "react";
import {Button, Segment, Table} from "semantic-ui-react";
import HOST from "./Constants";
import axios from "axios";

export class StatsView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            aggregate_by: "day",
            stats: [],
        };
        this.setAggregateBy = this.setAggregateBy.bind(this);
    }

    getStats(agg) {
        axios.get(HOST + '/api/stats', {params: {aggregate_by: agg}})
            .then((response) => {
                this.setState({stats: response.data})
            });
    }

    setAggregateBy(event) {
        this.setState({aggregate_by: event.target.name});
        this.getStats(event.target.name);
    }

    componentDidMount() {
        this.getStats(this.state.aggregate_by);
    }

    render() {
        return <div>
            <Segment basic>
                <Button primary={this.state.aggregate_by === "day"} name="day"
                        onClick={this.setAggregateBy}>Day</Button>
                <Button primary={this.state.aggregate_by === "month"} name="month"
                        onClick={this.setAggregateBy}>Month</Button>
            </Segment>
            <Segment basic>
                <Table>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>Day</Table.HeaderCell>
                            <Table.HeaderCell>Action</Table.HeaderCell>
                            <Table.HeaderCell textAlign="right">Duration [h]</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {this.state.stats.map((stat, index) =>
                            <Table.Row key={index}>
                                <Table.Cell>{stat.key}</Table.Cell>
                                <Table.Cell>{stat.action}</Table.Cell>
                                <Table.Cell textAlign="right">{(stat.duration / 3600).toFixed(2)}</Table.Cell>
                            </Table.Row>
                        )}
                    </Table.Body>
                </Table>
            </Segment>
        </div>;
    }
}