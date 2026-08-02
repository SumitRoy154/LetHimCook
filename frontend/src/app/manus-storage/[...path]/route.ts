import { type NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const key = path.join("/");
  if (!key) {
    return NextResponse.json({ error: "Missing storage key" }, { status: 400 });
  }

  const forgeBaseUrl = (process.env.BUILT_IN_FORGE_API_URL || "").replace(/\/+$/, "");
  const forgeKey = process.env.BUILT_IN_FORGE_API_KEY;

  if (!forgeBaseUrl || !forgeKey) {
    const fallbackSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600"><rect width="800" height="600" fill="#0a0a0a"/></svg>`;
    return new NextResponse(fallbackSvg, {
      headers: { "Content-Type": "image/svg+xml" },
    });
  }

  const forgeUrl = new URL("v1/storage/presign/get", `${forgeBaseUrl}/`);
  forgeUrl.searchParams.set("path", key);

  const forgeResp = await fetch(forgeUrl, {
    headers: {
      Authorization: `Bearer ${forgeKey}`,
    },
  });

  if (!forgeResp.ok) {
    return NextResponse.json({ error: "Storage backend error" }, { status: 502 });
  }

  const { url } = (await forgeResp.json()) as { url?: string };
  if (!url) {
    return NextResponse.json({ error: "Empty signed URL" }, { status: 502 });
  }

  return NextResponse.redirect(url, 307);
}
