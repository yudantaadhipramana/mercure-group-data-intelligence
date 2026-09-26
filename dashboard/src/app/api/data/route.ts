import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

export const dynamic = "force-static";
export const revalidate = false;

export async function GET() {
  const filePath = join(process.cwd(), "public", "dashboard_data.json");
  const text = await readFile(filePath, "utf-8");
  const dashboardData = JSON.parse(text);
  return NextResponse.json(dashboardData);
}
