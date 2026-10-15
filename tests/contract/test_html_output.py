"""Contract tests for the generated HTML output (T008)."""
import json
import re
from datetime import date

from timeline.models import ActivityGroup, Milestone, ScheduleDocument
from timeline.render_html import build_render_model, render_html


def _sample_doc() -> ScheduleDocument:
    g = ActivityGroup(name="การทบทวนและวางแผนงบประมาณ")
    g.milestones.append(
        Milestone(
            seq=1, date_text="๑ ต.ค. ๖๘", start_date=date(2025, 10, 1),
            owner="คณะรัฐมนตรี",
            description="พิจารณาให้ความเห็นชอบแนวทางการจัดทำงบประมาณฯ",
            group="การทบทวนและวางแผนงบประมาณ",
        )
    )
    doc = ScheduleDocument(
        path="HW03-Input.pdf", fiscal_year_be=2570,
        title="ปฏิทินงบประมาณรายจ่ายประจำปีงบประมาณ พ.ศ. ๒๕๗๐", groups=[g],
    )
    return doc


class TestRenderModel:
    def test_canvas_size(self):
        model = build_render_model(_sample_doc())
        assert model["canvas"] == {"width": 1200, "height": 675}

    def test_title_and_milestones(self):
        model = build_render_model(_sample_doc())
        assert "ปฏิทินงบประมาณ" in model["title"]
        assert len(model["milestones"]) == 1
        m = model["milestones"][0]
        assert m["seq"] == 1
        assert m["startDate"] == "2025-10-01"
        assert m["owner"] == "คณะรัฐมนตรี"
        assert m["group"] == "การทบทวนและวางแผนงบประมาณ"


class TestHtml:
    def test_single_file_canvas(self):
        html = render_html(build_render_model(_sample_doc()))
        assert "<canvas" in html
        assert 'width="1200"' in html and 'height="675"' in html
        assert "<script" in html

    def test_embeds_json(self):
        html = render_html(build_render_model(_sample_doc()))
        m = re.search(r"const DATA\s*=\s*(\{.*?\});", html, re.DOTALL)
        assert m, "embedded JSON not found"
        data = json.loads(m.group(1))
        assert data["title"].startswith("ปฏิทิน")
        assert data["milestones"]

    def test_no_external_resources(self):
        html = render_html(build_render_model(_sample_doc()))
        assert "http://" not in html and "https://" not in html
        assert "src=" not in html.replace("<script", "")
        assert "link rel" not in html

    def test_embedded_sarabun_font_and_arabic_display_digits(self):
        html = render_html(build_render_model(_sample_doc()))
        assert html.count("data:font/ttf;base64,") == 2
        assert 'font-family:"Sarabun Embedded"' in html
        assert "function arabicDigits(value)" in html
