from dataclasses import dataclass


@dataclass(frozen=True)
class TreeRenderStyle:
    """Shared tree render style and animation tuning values.

    Args:
        base_ground_color: RGB color for the grass layer under animated tree.
        trunk_color: RGB color for trunk fill.
        canopy_color: RGB color for canopy triangle.
        branch_color: RGB color for branch accent line.
        sway_speed_base: Base sway speed factor when wind is above zero.
        sway_speed_scale: Wind-driven sway speed multiplier.
        sway_amplitude_base: Minimum sway amplitude in pixels.
        sway_amplitude_scale: Wind-driven sway amplitude multiplier.
        phase_x_factor: X-axis contribution to per-tile sway phase offset.
        phase_y_factor: Y-axis contribution to per-tile sway phase offset.
        trunk_width_px: Trunk width in pixels.
        trunk_top_ratio: Fractional tile y where trunk begins.
        canopy_top_offset_px: Pixel offset from tile top for canopy tip.
        canopy_bottom_offset_px: Pixel offset from tile bottom for canopy base.
        canopy_half_width_px: Half-width of canopy base in pixels.
        branch_start_dx_px: Branch start x offset from canopy center.
        branch_end_dx_px: Branch end x offset from canopy center.
        branch_start_y_ratio: Branch start y ratio of tile size.
        branch_end_y_offset_px: Branch end extra y offset in pixels.

    Returns:
        None.
    """

    base_ground_color: tuple[int, int, int] = (126, 200, 80)
    trunk_color: tuple[int, int, int] = (110, 74, 48)
    canopy_color: tuple[int, int, int] = (38, 132, 65)
    branch_color: tuple[int, int, int] = (58, 160, 86)
    sway_speed_base: float = 1.2
    sway_speed_scale: float = 5.8
    sway_amplitude_base: float = 1.0
    sway_amplitude_scale: float = 10.0
    phase_x_factor: float = 0.37
    phase_y_factor: float = 0.23
    trunk_width_px: int = 4
    trunk_top_ratio: float = 0.5
    canopy_top_offset_px: int = 3
    canopy_bottom_offset_px: int = 4
    canopy_half_width_px: int = 8
    branch_start_dx_px: int = -3
    branch_end_dx_px: int = 4
    branch_start_y_ratio: float = 0.5
    branch_end_y_offset_px: int = 4


DEFAULT_TREE_STYLE = TreeRenderStyle()
