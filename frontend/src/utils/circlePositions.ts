/** Равномерное расположение точек по кругу (в процентах 0–100). */
export function circlePositions(
  count: number,
  cx = 50,
  cy = 52,
  radius = 26
): Array<{ x: number; y: number }> {
  const result: Array<{ x: number; y: number }> = [];
  for (let i = 0; i < count; i++) {
    const angleDeg = -90 + (360 / count) * i;
    const angleRad = (angleDeg * Math.PI) / 180;
    result.push({
      x: Math.round((cx + radius * Math.cos(angleRad)) * 10) / 10,
      y: Math.round((cy + radius * Math.sin(angleRad)) * 10) / 10,
    });
  }
  return result;
}
