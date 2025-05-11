import React from "react";

interface EquipButtonProps {
  characterName: string;
}

export function EquipButton({characterName}: EquipButtonProps) {
    return (
        <button>
            Equip
        </button>
    )
}