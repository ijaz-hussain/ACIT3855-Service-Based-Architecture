import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [health, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka-ijaz.eastus.cloudapp.azure.com/health/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 20000); // Update every 20 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health Stats</h1>
                <table className={"HealthTable"}>
					<tbody>
						<tr>
							<td>Receiver:</td>
                            <td>{health['receiver']}</td>
                        </tr>
                        <tr>
							<td>Storage:</td>
                            <td> {health['storage']}</td>
                        </tr>
                        <tr>
                            <td>Processing:</td>
                            <td>{health['processing']}</td>
                        </tr>
                        <tr>
                            <td>Audit:</td>
                            <td> {health['audit']}</td>
                        </tr>
                        <tr>
                            <td>Last Update:</td>
                            <td>{health['last_update']}</td>
						</tr>
					</tbody>
                </table>
            </div>
        )
    }
}
