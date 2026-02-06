import PropTypes from "prop-types";
import { BIOMECH_COLORS } from "../utils/skeletonStructure";
import "./BiomechLegend.css";

/**
 * Visual legend showing biomechanical quality color coding
 */
function BiomechLegend({ show = true }) {
    if (!show) return null;

    return (
        <div className="biomech-legend">
            <div className="legend-title">Biomechanical Quality</div>
            <div className="legend-items">
                <div className="legend-item">
                    <div
                        className="legend-color"
                        style={{ backgroundColor: BIOMECH_COLORS.excellent }}
                    />
                    <span>Excellent</span>
                </div>
                <div className="legend-item">
                    <div
                        className="legend-color"
                        style={{ backgroundColor: BIOMECH_COLORS.good }}
                    />
                    <span>Good</span>
                </div>
                <div className="legend-item">
                    <div
                        className="legend-color"
                        style={{ backgroundColor: BIOMECH_COLORS.needs_work }}
                    />
                    <span>Needs Work</span>
                </div>
                <div className="legend-item">
                    <div
                        className="legend-color"
                        style={{ backgroundColor: BIOMECH_COLORS.poor }}
                    />
                    <span>Poor</span>
                </div>
            </div>
        </div>
    );
}

BiomechLegend.propTypes = {
    show: PropTypes.bool,
};

export default BiomechLegend;
