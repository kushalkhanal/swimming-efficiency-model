import PropTypes from 'prop-types';
import './ComparisonMetrics.css';

/**
 * Display comparison metrics between two swimming sessions
 */
function ComparisonMetrics({ leftMetrics, rightMetrics }) {
    // Calculate stroke rate if available
    const calculateStrokeRate = (metrics) => {
        if (!metrics?.velocities?.hand_left || !metrics?.velocities?.hand_right) {
            return 'N/A';
        }

        // Simplified stroke rate calculation
        // Count peaks in hand velocity (indicates stroke cycles)
        const leftVel = metrics.velocities.hand_left;
        const rightVel = metrics.velocities.hand_right;

        if (leftVel.length === 0) return 'N/A';

        // Estimate strokes per minute
        const avgVelocity = leftVel.reduce((a, b) => a + b, 0) / leftVel.length;
        const strokeRate = Math.round(avgVelocity * 60); // Simplified calculation

        return `${strokeRate} SPM`;
    };

    const leftStrokeRate = calculateStrokeRate(leftMetrics);
    const rightStrokeRate = calculateStrokeRate(rightMetrics);

    // Calculate average joint angles
    const calculateAvgAngle = (metrics, joint) => {
        if (!metrics?.joint_angles?.[joint]) return 'N/A';
        const angles = metrics.joint_angles[joint];
        if (angles.length === 0) return 'N/A';
        const avg = angles.reduce((a, b) => a + b, 0) / angles.length;
        return `${Math.round(avg)}°`;
    };

    const metrics = [
        {
            name: 'Stroke Rate',
            left: leftStrokeRate,
            right: rightStrokeRate,
            unit: '',
        },
        {
            name: 'Left Elbow Angle (Avg)',
            left: calculateAvgAngle(leftMetrics, 'elbow_left'),
            right: calculateAvgAngle(rightMetrics, 'elbow_left'),
            unit: '',
        },
        {
            name: 'Right Elbow Angle (Avg)',
            left: calculateAvgAngle(leftMetrics, 'elbow_right'),
            right: calculateAvgAngle(rightMetrics, 'elbow_right'),
            unit: '',
        },
        {
            name: 'Left Shoulder Angle (Avg)',
            left: calculateAvgAngle(leftMetrics, 'shoulder_left'),
            right: calculateAvgAngle(rightMetrics, 'shoulder_left'),
            unit: '',
        },
    ];

    return (
        <div className="comparison-metrics">
            <h3>Performance Comparison</h3>
            <table className="metrics-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Your Session</th>
                        <th>Gold Standard</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
                    {metrics.map((metric, idx) => {
                        const leftVal = parseFloat(metric.left);
                        const rightVal = parseFloat(metric.right);
                        const diff = !isNaN(leftVal) && !isNaN(rightVal)
                            ? (leftVal - rightVal).toFixed(1)
                            : 'N/A';

                        const diffClass = diff === 'N/A' ? '' :
                            Math.abs(parseFloat(diff)) < 5 ? 'close' :
                                parseFloat(diff) < 0 ? 'below' : 'above';

                        return (
                            <tr key={idx}>
                                <td className="metric-name">{metric.name}</td>
                                <td>{metric.left}</td>
                                <td>{metric.right}</td>
                                <td className={`diff ${diffClass}`}>
                                    {diff !== 'N/A' && (diff > 0 ? '+' : '')}{diff}{diff !== 'N/A' && metric.unit}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

ComparisonMetrics.propTypes = {
    leftMetrics: PropTypes.object,
    rightMetrics: PropTypes.object,
};

export default ComparisonMetrics;
