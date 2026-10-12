import { WrenchIcon } from "lucide-react"

import { TOOLS } from "@/presentation/constants/tools/constants"
import type { ToolInfo } from "@/presentation/types/tools/types"

export const toolInfo = (tool: string): ToolInfo => TOOLS[tool] ?? { action: tool, name: tool, icon: WrenchIcon }
