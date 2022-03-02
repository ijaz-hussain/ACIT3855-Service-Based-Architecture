import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka-ijaz.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Acceleration Reading</th>
							<th>Environmental Reading</th>
						</tr>
						<tr>
							<td># of Acceleration Readings: {stats['num_acceleration_readings']}</td>
							<td># of Environmental Readings: {stats['num_environmental_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Acceleration Speed Reading: {stats['max_acceleration_speed_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Acceleration Watt Hours Reading: {stats['max_acceleration_watt_hours_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Temperature Reading: {stats['max_temp_reading']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
