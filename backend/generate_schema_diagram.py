from __future__ import annotations

from pathlib import Path
import sys
import types

from PIL import Image, ImageDraw, ImageFont

if "dotenv" not in sys.modules:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_stub

from app.db import Base
import app.models  # noqa: F401  # Ensure models are registered on Base.metadata


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "db_schema_design.png"

CANVAS_WIDTH = 2600
CANVAS_HEIGHT = 1900
MARGIN = 40
BOX_WIDTH = 360
ROW_HEIGHT = 28
HEADER_HEIGHT = 40
PADDING = 12

COLORS = {
    "bg_top": "#f7fafc",
    "bg_bottom": "#e8f0ff",
    "title": "#102a43",
    "subtitle": "#486581",
    "box_fill": "#ffffff",
    "box_border": "#9fb3c8",
    "header_fill": "#1f6feb",
    "header_text": "#ffffff",
    "row_text": "#243b53",
    "fk_line": "#d64545",
    "pk_fill": "#e6f4ea",
    "fk_fill": "#fff3cd",
    "legend_border": "#bcccdc",
}


LAYOUT = {
    "users": (60, 110),
    "categories": (470, 110),
    "customers": (880, 110),
    "milk_subscribers": (1290, 110),
    "suppliers": (1700, 110),
    "products": (470, 520),
    "expenses": (60, 520),
    "sales": (880, 520),
    "milk_delivery_entries": (1290, 520),
    "supplier_payments": (1700, 520),
    "stock_movements": (60, 1040),
    "sale_items": (880, 1040),
    "credit_transactions": (1290, 1040),
    "damage_loss_records": (470, 1040),
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(["arialbd.ttf", "DejaVuSans-Bold.ttf"])
    else:
        candidates.extend(["arial.ttf", "DejaVuSans.ttf"])

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(34, bold=True)
FONT_SUBTITLE = load_font(18)
FONT_HEADER = load_font(18, bold=True)
FONT_BODY = load_font(14)
FONT_LEGEND = load_font(16)


def make_background() -> Image.Image:
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), COLORS["bg_top"])
    pixels = image.load()
    for y in range(CANVAS_HEIGHT):
        ratio = y / max(CANVAS_HEIGHT - 1, 1)
        top = tuple(int(COLORS["bg_top"][i : i + 2], 16) for i in (1, 3, 5))
        bottom = tuple(int(COLORS["bg_bottom"][i : i + 2], 16) for i in (1, 3, 5))
        mixed = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        for x in range(CANVAS_WIDTH):
            pixels[x, y] = mixed
    return image


def column_label(column) -> str:
    flags = []
    if column.primary_key:
        flags.append("PK")
    if column.foreign_keys:
        flags.append("FK")
    flags_text = f"[{'/'.join(flags)}] " if flags else ""
    type_name = str(column.type)
    nullable = "" if not column.nullable or column.primary_key else " ?"
    return f"{flags_text}{column.name}: {type_name}{nullable}"


def table_height(table) -> int:
    return HEADER_HEIGHT + (len(table.columns) * ROW_HEIGHT) + (PADDING * 2)


def draw_table(draw: ImageDraw.ImageDraw, table, position: tuple[int, int]) -> dict[str, tuple[int, int]]:
    x, y = position
    height = table_height(table)
    draw.rounded_rectangle(
        (x, y, x + BOX_WIDTH, y + height),
        radius=18,
        fill=COLORS["box_fill"],
        outline=COLORS["box_border"],
        width=2,
    )
    draw.rounded_rectangle(
        (x, y, x + BOX_WIDTH, y + HEADER_HEIGHT),
        radius=18,
        fill=COLORS["header_fill"],
        outline=COLORS["header_fill"],
    )
    draw.rectangle((x, y + 20, x + BOX_WIDTH, y + HEADER_HEIGHT), fill=COLORS["header_fill"])
    draw.text((x + PADDING, y + 9), table.name, font=FONT_HEADER, fill=COLORS["header_text"])

    anchors: dict[str, tuple[int, int]] = {}
    row_y = y + HEADER_HEIGHT + PADDING
    for column in table.columns:
        line_box = (x + 8, row_y - 2, x + BOX_WIDTH - 8, row_y + ROW_HEIGHT - 2)
        if column.primary_key:
            draw.rounded_rectangle(line_box, radius=8, fill=COLORS["pk_fill"])
        elif column.foreign_keys:
            draw.rounded_rectangle(line_box, radius=8, fill=COLORS["fk_fill"])
        draw.text((x + PADDING + 2, row_y + 4), column_label(column), font=FONT_BODY, fill=COLORS["row_text"])
        anchors[column.name] = (x + BOX_WIDTH, row_y + 12)
        row_y += ROW_HEIGHT

    return anchors


def draw_connection(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str,
) -> None:
    sx, sy = start
    ex, ey = end
    mid_x = sx + ((ex - sx) // 2)
    points = [(sx, sy), (mid_x, sy), (mid_x, ey), (ex, ey)]
    draw.line(points, fill=COLORS["fk_line"], width=3)
    arrow = 8
    draw.polygon([(ex, ey), (ex - arrow, ey - arrow // 2), (ex - arrow, ey + arrow // 2)], fill=COLORS["fk_line"])
    label_x = min(max(mid_x + 6, MARGIN), CANVAS_WIDTH - 240)
    label_y = min(sy, ey) + abs(ey - sy) // 2 - 10
    draw.rounded_rectangle(
        (label_x - 4, label_y - 2, label_x + 170, label_y + 18),
        radius=6,
        fill="#ffffff",
        outline=COLORS["legend_border"],
    )
    draw.text((label_x, label_y), label, font=FONT_BODY, fill=COLORS["fk_line"])


def main() -> None:
    tables = {table.name: table for table in Base.metadata.sorted_tables}
    image = make_background()
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN, 28), "Sonik Backend Database Schema", font=FONT_TITLE, fill=COLORS["title"])
    draw.text(
        (MARGIN, 72),
        "Generated from SQLAlchemy models in backend/app/models.py",
        font=FONT_SUBTITLE,
        fill=COLORS["subtitle"],
    )

    anchors_by_table: dict[str, dict[str, tuple[int, int]]] = {}
    left_edge_targets: dict[str, tuple[int, int]] = {}

    for table_name, table in tables.items():
        if table_name not in LAYOUT:
            continue
        x, y = LAYOUT[table_name]
        anchors_by_table[table_name] = draw_table(draw, table, (x, y))
        left_edge_targets[table_name] = (x, y + HEADER_HEIGHT + 24)

    for table_name, table in tables.items():
        if table_name not in anchors_by_table:
            continue
        for column in table.columns:
            for fk in column.foreign_keys:
                referred_table = fk.column.table.name
                referred_column = fk.column.name
                if referred_table not in anchors_by_table:
                    continue
                start = anchors_by_table[table_name][column.name]
                target_anchor = anchors_by_table[referred_table].get(referred_column, left_edge_targets[referred_table])
                end = (LAYOUT[referred_table][0], target_anchor[1])
                draw_connection(draw, start, end, f"{table_name}.{column.name}")

    legend_x = 2040
    legend_y = 1320
    draw.rounded_rectangle(
        (legend_x, legend_y, legend_x + 470, legend_y + 210),
        radius=18,
        fill="#ffffff",
        outline=COLORS["legend_border"],
        width=2,
    )
    draw.text((legend_x + 20, legend_y + 18), "Legend", font=FONT_HEADER, fill=COLORS["title"])
    draw.rounded_rectangle((legend_x + 20, legend_y + 60, legend_x + 50, legend_y + 88), radius=6, fill=COLORS["pk_fill"])
    draw.text((legend_x + 65, legend_y + 63), "Primary key row", font=FONT_LEGEND, fill=COLORS["row_text"])
    draw.rounded_rectangle((legend_x + 20, legend_y + 105, legend_x + 50, legend_y + 133), radius=6, fill=COLORS["fk_fill"])
    draw.text((legend_x + 65, legend_y + 108), "Foreign key row", font=FONT_LEGEND, fill=COLORS["row_text"])
    draw.line((legend_x + 20, legend_y + 160, legend_x + 50, legend_y + 160), fill=COLORS["fk_line"], width=3)
    draw.polygon(
        [(legend_x + 50, legend_y + 160), (legend_x + 42, legend_y + 156), (legend_x + 42, legend_y + 164)],
        fill=COLORS["fk_line"],
    )
    draw.text((legend_x + 65, legend_y + 149), "Relationship from FK to referenced PK", font=FONT_LEGEND, fill=COLORS["row_text"])

    image.save(OUTPUT_PATH, format="PNG")
    print(f"Schema diagram written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
