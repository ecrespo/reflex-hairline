/*
 * reflex-hairline: the two React components the Python package needs beyond
 * the twenty-seven that @lucasmarkes/hairline/react already exports.
 *
 *   HairlineFigure  picks one of the twenty-seven by name at runtime, so a
 *                   Reflex state var can switch figures.
 *   HairlineCustom  mounts a figure made with the hairline-create skill: a
 *                   `hairline-<name>.html` page or its `<name>.js` figure file.
 *                   It runs the figure on the same kernel the skill builds on,
 *                   with the same options as the packaged figures.
 *
 * Plain JS (no JSX) so it can be imported straight from the app's public dir.
 */
import { createElement, useEffect, useRef } from "react";
import * as Figures from "@lucasmarkes/hairline/react";

/* ------------------------------------------------------------------------ */
/* HairlineFigure                                                           */
/* ------------------------------------------------------------------------ */

const componentFor = (name) => {
  const id = String(name ?? "").trim().toLowerCase();
  const key = id.charAt(0).toUpperCase() + id.slice(1);
  return [id, Figures[key]];
};

/** One of the packaged figures, chosen by its id ("terrain", "riffle", ...). */
export function HairlineFigure({ figure = "terrain", fallback = "terrain", ...props }) {
  let [id, Component] = componentFor(figure);
  if (typeof Component !== "object" && typeof Component !== "function") {
    [id, Component] = componentFor(fallback);
  }
  if (!Component) return null;
  /* a different figure is a different drawing: the key remounts it */
  return createElement(Component, { key: id, ...props });
}

/* ------------------------------------------------------------------------ */
/* HairlineCustom                                                           */
/* ------------------------------------------------------------------------ */

let kernelPromise = null;
const loadKernel = () => {
  if (!kernelPromise) kernelPromise = import("./hairline_kernel.js").then((m) => m.default);
  return kernelPromise;
};

const FIGURE_SCRIPT = /<script[^>]*\bid=["']hl-figure["'][^>]*>([\s\S]*?)<\/script>/i;
/** The figure's own code: the hl-figure script of a page the skill built, or the text as it is. */
const extract = (text) => {
  const m = FIGURE_SCRIPT.exec(text);
  return m ? m[1] : text;
};

const sources = new Map();
const loadSource = (src, code) => {
  if (typeof code === "string" && code.trim() !== "") return Promise.resolve(extract(code));
  if (!src) return Promise.reject(new Error("hairline: custom() needs `src` or `code`."));
  if (!sources.has(src)) {
    sources.set(
      src,
      fetch(src)
        .then((r) => {
          if (!r.ok) throw new Error(`hairline: could not load ${src} (HTTP ${r.status}).`);
          return r.text();
        })
        .then(extract)
        .catch((err) => {
          sources.delete(src);
          throw err;
        }),
    );
  }
  return sources.get(src);
};

/** Runs the figure's code with the kernel and catches what it declares through hairline({...}). */
const define = (HL, code) => {
  let spec = null;
  // eslint-disable-next-line no-new-func
  new Function("HL", "hairline", `"use strict";\n${code}`)(HL, (s) => {
    spec = s;
  });
  if (!spec || typeof spec.mount !== "function") {
    throw new Error("hairline: the figure never called hairline({ name, means, range, mount }).");
  }
  return spec;
};

const clampIntensity = (value) => {
  const n = typeof value === "string" && value.trim() !== "" ? Number(value) : value;
  if (typeof n !== "number" || !Number.isFinite(n)) return 0.5;
  return Math.min(1, Math.max(0, n));
};

/** The figure's own number for an intensity: two straight lines that meet at 0.5, as in the package. */
const parameter = (range, value) => {
  const [lo, mid, hi] = Array.isArray(range) && range.length === 3 ? range : [0, 0.5, 1];
  const i = clampIntensity(value);
  const v = i <= 0.5 ? lo + (i / 0.5) * (mid - lo) : mid + ((i - 0.5) / 0.5) * (hi - mid);
  return Math.round(v * 1000) / 1000;
};

const report = (err) => {
  if (typeof reportError === "function") reportError(err);
  else setTimeout(() => { throw err; });
};

/** Attributes a mounted figure owns, removed again on unmount. */
const OWNED = ["data-hairline", "data-hairline-theme", "role"];

const dress = (host, spec, { theme, label }) => {
  if (theme === "light" || theme === "dark") host.setAttribute("data-hairline-theme", theme);
  else host.removeAttribute("data-hairline-theme");
  if (!host.hasAttribute("aria-labelledby")) {
    host.setAttribute("aria-label", typeof label === "string" && label ? label : spec?.means ?? "A Hairline figure");
  }
};

/** A figure made with the hairline-create skill, mounted like a packaged one. */
export function HairlineCustom({
  src,
  code,
  intensity,
  theme,
  label,
  onRead,
  onLoad,
  onError,
  style,
  ...rest
}) {
  const host = useRef(null);
  const handle = useRef(null);
  const spec = useRef(null);
  const latest = useRef({ intensity, theme, label });
  const callbacks = useRef({ onRead, onLoad, onError });

  latest.current = { intensity, theme, label };
  callbacks.current = { onRead, onLoad, onError };

  useEffect(() => {
    const el = host.current;
    if (!el) return undefined;
    let cancelled = false;
    let figure = null;
    let svg = null;

    Promise.all([loadKernel(), loadSource(src, code)])
      .then(([HL, text]) => {
        if (cancelled) return;
        const declared = define(HL, text);
        spec.current = declared;

        const root = el.getRootNode();
        HL.inject(root && (root.nodeType === 9 || "host" in root) ? root : document);
        el.setAttribute("data-hairline", String(declared.name || "custom"));
        el.setAttribute("role", "img");
        el.removeAttribute("data-hairline-error");
        dress(el, declared, latest.current);

        svg = HL.mk("svg", { viewBox: "0 0 400 320", "aria-hidden": "true" }, el);

        let caption = null;
        const read = {
          get textContent() { return caption; },
          set textContent(value) {
            const next = value == null ? "" : String(value);
            if (next === caption) return;
            caption = next;
            const fn = callbacks.current.onRead;
            if (typeof fn === "function") {
              try { fn(next); } catch (err) { report(err); }
            }
          },
        };

        figure = declared.mount({ stage: el, svg, read }, parameter(declared.range, latest.current.intensity));
        handle.current = figure;
        if (caption === null) read.textContent = "rest";

        const loaded = callbacks.current.onLoad;
        if (typeof loaded === "function") {
          loaded({
            name: String(declared.name ?? ""),
            means: String(declared.means ?? ""),
            rules: Array.isArray(declared.rules) ? declared.rules : [],
            range: Array.isArray(declared.range) ? declared.range : [],
          });
        }
      })
      .catch((err) => {
        if (cancelled) return;
        const message = String((err && err.message) || err);
        el.setAttribute("data-hairline-error", message);
        console.error(err);
        const fn = callbacks.current.onError;
        if (typeof fn === "function") fn(message);
      });

    return () => {
      cancelled = true;
      try { figure?.destroy?.(); } catch (err) { report(err); }
      svg?.remove();
      handle.current = null;
      spec.current = null;
      for (const name of OWNED) el.removeAttribute(name);
    };
  }, [src, code]);

  useEffect(() => {
    if (handle.current && spec.current) handle.current.set?.(parameter(spec.current.range, intensity));
  }, [intensity]);

  useEffect(() => {
    if (spec.current && host.current) dress(host.current, spec.current, { theme, label });
  }, [theme, label]);

  return createElement("div", {
    ...rest,
    ref: host,
    style: { aspectRatio: "5 / 4", ...style },
  });
}
