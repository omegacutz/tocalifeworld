from dataclasses import dataclass


@dataclass(frozen=True)
class AvatarRenderStyle:
    """Shared avatar render style values used by renderer.

    Args:
        skin_color: RGB tone for face/head drawing.
        limb_color: RGB tone for arms and legs.
        shoe_color: RGB tone for shoes.
        body_w: Body width in pixels.
        body_h: Body height in pixels.
        head_radius: Head circle radius in pixels.
        player_hat_width: Hat width used for player avatars.
        npc_hat_width: Hat width used for NPC avatars.

    Returns:
        None.
    """

    skin_color: tuple[int, int, int] = (241, 194, 125)
    limb_color: tuple[int, int, int] = (82, 58, 45)
    shoe_color: tuple[int, int, int] = (44, 44, 44)
    body_w: int = 8
    body_h: int = 9
    head_radius: int = 4
    player_hat_width: int = 10
    npc_hat_width: int = 9


DEFAULT_AVATAR_STYLE = AvatarRenderStyle()
