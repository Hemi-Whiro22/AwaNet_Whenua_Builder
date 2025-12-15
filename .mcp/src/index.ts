#!/usr/bin/env node
/**
 * AwaOS MCP Server
 * 
 * Model Context Protocol server for IDE integration with AwaOS.
 * Provides tools for realm management, pipeline execution, and memory search.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync, spawn } from "child_process";
import { existsSync, readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

// AwaOS paths
const AWANET_PATH = process.env.AWANET_PATH || join(homedir(), ".awanet");
const PROJECTS_PATH = join(AWANET_PATH, "projects");
const CONFIG_PATH = join(AWANET_PATH, "config");

/**
 * Execute Te Hau CLI command
 */
function tehau(args: string[]): string {
  try {
    const result = execSync(`tehau ${args.join(" ")}`, {
      encoding: "utf-8",
      cwd: AWANET_PATH,
    });
    return result;
  } catch (error: any) {
    return error.message || "Command failed";
  }
}

/**
 * Read JSON file safely
 */
function readJson(path: string): any {
  try {
    if (existsSync(path)) {
      return JSON.parse(readFileSync(path, "utf-8"));
    }
  } catch {}
  return null;
}

/**
 * Get current realm context
 */
function getCurrentRealm(): string | null {
  const contextPath = join(CONFIG_PATH, "context.json");
  const context = readJson(contextPath);
  return context?.current_realm || null;
}

/**
 * List all realms
 */
function listRealms(): string[] {
  try {
    if (existsSync(PROJECTS_PATH)) {
      const { readdirSync, statSync } = require("fs");
      return readdirSync(PROJECTS_PATH).filter((name: string) => {
        const path = join(PROJECTS_PATH, name);
        return statSync(path).isDirectory();
      });
    }
  } catch {}
  return [];
}

/**
 * Get realm info
 */
function getRealmInfo(realmName: string): any {
  const realmPath = join(PROJECTS_PATH, realmName);
  const realmLock = readJson(join(realmPath, "mauri", "realm_lock.json"));
  const glyphManifest = readJson(join(realmPath, "mauri", "glyph_manifest.json"));
  
  return {
    name: realmName,
    path: realmPath,
    exists: existsSync(realmPath),
    realm_lock: realmLock,
    glyph: glyphManifest,
    namespace: `realm::${realmName}`,
  };
}

// Create MCP Server
const server = new Server(
  {
    name: "awaos-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
      prompts: {},
    },
  }
);

// Tool definitions
const TOOLS = [
  {
    name: "realm_info",
    description: "Get information about the current or specified realm",
    inputSchema: {
      type: "object" as const,
      properties: {
        realm: {
          type: "string",
          description: "Realm name (optional, uses current if not specified)",
        },
      },
    },
  },
  {
    name: "realm_list",
    description: "List all available realms",
    inputSchema: {
      type: "object" as const,
      properties: {},
    },
  },
  {
    name: "realm_switch",
    description: "Switch to a different realm context",
    inputSchema: {
      type: "object" as const,
      properties: {
        realm: {
          type: "string",
          description: "Realm name to switch to",
        },
      },
      required: ["realm"],
    },
  },
  {
    name: "pipeline_run",
    description: "Execute a pipeline in the current realm",
    inputSchema: {
      type: "object" as const,
      properties: {
        pipeline: {
          type: "string",
          description: "Pipeline name (embed, summarise, translate, taonga)",
        },
        input: {
          type: "string",
          description: "Input text or file path",
        },
        realm: {
          type: "string",
          description: "Realm name (optional)",
        },
      },
      required: ["pipeline", "input"],
    },
  },
  {
    name: "pipeline_list",
    description: "List available pipelines for a realm",
    inputSchema: {
      type: "object" as const,
      properties: {
        realm: {
          type: "string",
          description: "Realm name (optional)",
        },
      },
    },
  },
  {
    name: "seal_verify",
    description: "Verify the seal/integrity of a realm",
    inputSchema: {
      type: "object" as const,
      properties: {
        realm: {
          type: "string",
          description: "Realm name to verify",
        },
      },
      required: ["realm"],
    },
  },
  {
    name: "kaitiaki_invoke",
    description: "Invoke a kaitiaki (AI guardian) with a prompt",
    inputSchema: {
      type: "object" as const,
      properties: {
        name: {
          type: "string",
          description: "Kaitiaki name (kitenga_whiro, ruru, ahiatoa, maruao)",
        },
        prompt: {
          type: "string",
          description: "Prompt for the kaitiaki",
        },
        realm: {
          type: "string",
          description: "Realm context (optional)",
        },
      },
      required: ["name", "prompt"],
    },
  },
  {
    name: "kaitiaki_list",
    description: "List available kaitiaki",
    inputSchema: {
      type: "object" as const,
      properties: {},
    },
  },
];

// Prompt definitions
const PROMPTS = [
  {
    name: "realm_context",
    description: "Get context about the current realm for AI assistants",
    arguments: [
      {
        name: "realm",
        description: "Realm name (optional)",
        required: false,
      },
    ],
  },
  {
    name: "kaitiaki_guidance",
    description: "Get guidance from a specific kaitiaki",
    arguments: [
      {
        name: "kaitiaki",
        description: "Kaitiaki name",
        required: true,
      },
      {
        name: "topic",
        description: "Topic to get guidance on",
        required: true,
      },
    ],
  },
];

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "realm_info": {
      const realm = (args?.realm as string) || getCurrentRealm();
      if (!realm) {
        return { content: [{ type: "text", text: "No realm specified or active" }] };
      }
      const info = getRealmInfo(realm);
      return { content: [{ type: "text", text: JSON.stringify(info, null, 2) }] };
    }

    case "realm_list": {
      const realms = listRealms();
      const current = getCurrentRealm();
      const output = realms.map((r) => (r === current ? `* ${r}` : `  ${r}`)).join("\n");
      return { content: [{ type: "text", text: `Available realms:\n${output}` }] };
    }

    case "realm_switch": {
      const realm = args?.realm as string;
      const result = tehau(["context", "--switch", realm]);
      return { content: [{ type: "text", text: result }] };
    }

    case "pipeline_run": {
      const pipeline = args?.pipeline as string;
      const input = args?.input as string;
      const realm = (args?.realm as string) || getCurrentRealm();
      if (!realm) {
        return { content: [{ type: "text", text: "No realm specified or active" }] };
      }
      const result = tehau(["pipeline", realm, pipeline, "--input", input]);
      return { content: [{ type: "text", text: result }] };
    }

    case "pipeline_list": {
      const realm = (args?.realm as string) || getCurrentRealm();
      if (!realm) {
        return { content: [{ type: "text", text: "No realm specified or active" }] };
      }
      const result = tehau(["pipelines", realm]);
      return { content: [{ type: "text", text: result }] };
    }

    case "seal_verify": {
      const realm = args?.realm as string;
      const result = tehau(["seal", "--verify", "--realm", realm]);
      return { content: [{ type: "text", text: result }] };
    }

    case "kaitiaki_invoke": {
      const kaitiakiName = args?.name as string;
      const prompt = args?.prompt as string;
      const realm = args?.realm as string;
      const cmdArgs = ["kaitiaki", "invoke", kaitiakiName, "--prompt", `"${prompt}"`];
      if (realm) cmdArgs.push("--realm", realm);
      const result = tehau(cmdArgs);
      return { content: [{ type: "text", text: result }] };
    }

    case "kaitiaki_list": {
      const result = tehau(["kaitiaki", "list"]);
      return { content: [{ type: "text", text: result }] };
    }

    default:
      return { content: [{ type: "text", text: `Unknown tool: ${name}` }] };
  }
});

// Handle prompt listing
server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: PROMPTS,
}));

// Handle prompt retrieval
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "realm_context": {
      const realm = (args?.realm as string) || getCurrentRealm();
      if (!realm) {
        return {
          messages: [
            {
              role: "user" as const,
              content: { type: "text" as const, text: "No realm context available." },
            },
          ],
        };
      }
      const info = getRealmInfo(realm);
      return {
        messages: [
          {
            role: "user" as const,
            content: {
              type: "text" as const,
              text: `Current AwaOS Realm Context:
              
Realm: ${info.name}
Namespace: ${info.namespace}
Path: ${info.path}
Sealed: ${info.realm_lock?.sealed || false}

This is a sovereign AI operating system for cultural compute.
The realm contains te_ao (frontend), mini_te_po (backend), and mauri (identity) components.

Available pipelines: embed, summarise, translate, taonga
Available kaitiaki: Kitenga Whiro (Navigator), Ruru (Librarian), Ahiatoa (Translator), Maruao (Memory Guardian)`,
            },
          },
        ],
      };
    }

    case "kaitiaki_guidance": {
      const kaitiaki = args?.kaitiaki as string;
      const topic = args?.topic as string;
      return {
        messages: [
          {
            role: "user" as const,
            content: {
              type: "text" as const,
              text: `Seeking guidance from ${kaitiaki} on: ${topic}
              
Please provide guidance in the style of the ${kaitiaki} kaitiaki.`,
            },
          },
        ],
      };
    }

    default:
      return {
        messages: [
          {
            role: "user" as const,
            content: { type: "text" as const, text: `Unknown prompt: ${name}` },
          },
        ],
      };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("AwaOS MCP Server running on stdio");
}

main().catch(console.error);
