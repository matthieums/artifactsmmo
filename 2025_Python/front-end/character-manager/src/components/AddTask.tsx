import React from "react";

interface AddTaskProps {
  characterIndex: number;
}

export function AddTask({characterIndex}: AddTaskProps) {
    return (
        <button onClick={onclickHandler}>
            Add task
        </button>
    )

    async function onclickHandler() {
        const taskPayload = {
            iterations: 1,
            character_index: characterIndex,
            function: "gather",
            args: [],
            kwargs: {
                quantity: 2,
                resource: "copper_ore"
            }
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskPayload)
            });

            const result = await response.json();
            console.log(result);
        } catch (error) {
            console.error("Error submitting task:", error);
        }

    }
}