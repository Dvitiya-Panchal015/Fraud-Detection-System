import React from "react";

const hourlyVolume = [
  42, 31, 24, 18, 16, 22, 38, 61, 78, 84, 73, 69, 76, 82, 91, 96, 88, 94, 100,
  86, 72, 67, 59, 48,
];
const numberFormat = new Intl.NumberFormat("en-IN");
const maximum = Math.max(...hourlyVolume);

export default function HourlyVolumeChart() {
  return (
    <div
      className="hourly-chart"
      role="img"
      aria-label="Illustrative demo transaction volume by hour, with the highest volume at 18:00"
    >
      <div className="hourly-bars">
        {hourlyVolume.map((volume, hour) => (
          <div className="hourly-bar-column" key={hour}>
            <span
              className="hourly-bar"
              style={{ height: `${(volume / maximum) * 100}%` }}
              title={`${hour.toString().padStart(2, "0")}:00 · ${numberFormat.format(volume)} demo transactions`}
            />
            {hour % 3 === 0 && (
              <span className="hourly-label">
                {hour.toString().padStart(2, "0")}
              </span>
            )}
          </div>
        ))}
      </div>
      <div className="hourly-axis">
        <span>00:00</span>
        <span>Hour of day</span>
        <span>23:00</span>
      </div>
      <p className="chart-note">
        Illustrative demo profile. The current analytics API does not provide
        transaction-volume aggregates by hour.
      </p>
    </div>
  );
}
