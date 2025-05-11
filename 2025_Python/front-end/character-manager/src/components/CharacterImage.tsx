import React from "react"

interface CharacterImageProps {
    source: string
}

export function CharacterImage( {source}: CharacterImageProps ) {

    return (
        <div>
            <img src={source} alt="" />
        </div>
    )
}