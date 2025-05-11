import React from "react";
import { Task } from "../types/task"

interface TaskQueueViewerProps {
  queue: Task[];
}

export function TaskQueueViewer({ queue }: TaskQueueViewerProps) {

    return (
        <p>{queue.map(task => task.taskName).join(" - ")}</p>
  );
}
