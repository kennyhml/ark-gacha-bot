from dataclasses import dataclass

@dataclass
class Buff:
    name: str
    image: str

hungry = Buff("Hungry", "templates/hungry.png")
thirsty = Buff("Thirsty", "templates/thirsty.png")
pod_xp = Buff("XP Buff", "templates/pod_buff.png")
broken_bones = Buff("Broken Bones", "templates/broken_bones.png")