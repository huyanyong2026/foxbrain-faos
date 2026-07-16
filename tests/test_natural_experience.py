import importlib.util
import io
import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path


TEST_APP_DIR = tempfile.mkdtemp(prefix="foxbrain-natural-")
os.environ["APP_DIR"] = TEST_APP_DIR
os.environ["SAP_SUMMARY_FILE"] = str(Path(TEST_APP_DIR) / "missing-summary.json")
SPEC = importlib.util.spec_from_file_location(
    "foxbrain_portal_natural_test",
    Path(__file__).resolve().parents[1] / "portal_v2.py",
)
portal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portal)


class NaturalExperienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        portal.init()
        now = int(time.time())
        with portal.db() as conn:
            conn.execute(
                "insert into users(email,name,phone,store,role,status,password_hash,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                ("natural@example.test", "测试老板", "", "总部", "admin", "approved", portal.hp("test-only-password"), now, now),
            )

    def setUp(self):
        self.app = object.__new__(portal.App)
        with portal.db() as conn:
            conn.execute("delete from timeline_events")
            conn.execute("delete from tasks")
            conn.execute("delete from copilot_messages")
            conn.execute("delete from copilot_sessions")
            conn.execute("delete from decision_outcomes")
            conn.execute("delete from agent_learning_feedback")
            conn.execute("delete from enterprise_training_samples")
            conn.execute("delete from ai_agent_runs")
            conn.execute("delete from enterprise_relationships")
            conn.execute("delete from enterprise_entity_registry")
            conn.execute("delete from manual_business_report_publications")
            self.user = conn.execute("select * from users where email=?", ("natural@example.test",)).fetchone()

    def test_page_context_is_clean_and_bounded(self):
        context = self.app.copilot_page_context(
            {"ctx_page": "/brand-intelligence", "ctx_title": "Osprey 品牌分析", "ignored": "x"}
        )
        self.assertEqual(context["page"], "/brand-intelligence")
        self.assertEqual(context["title"], "Osprey 品牌分析")
        self.assertNotIn("ignored", context)

    def test_follow_up_reuses_session_and_keeps_context(self):
        first, first_code = self.app.create_copilot_answer(
            self.user,
            "这个品牌现在怎么样？",
            "",
            "",
            {"page": "/brand-intelligence", "title": "Osprey 品牌分析", "name": "Osprey"},
        )
        second, second_code = self.app.create_copilot_answer(
            self.user,
            "为什么？下一步做什么？",
            "",
            str(first["session_id"]),
            {"page": "/brand-intelligence", "title": "Osprey 品牌分析", "name": "Osprey"},
        )
        self.assertEqual(first_code, 200)
        self.assertEqual(second_code, 200)
        self.assertEqual(second["session_id"], first["session_id"])
        with portal.db() as conn:
            self.assertEqual(conn.execute("select count(*) from copilot_sessions").fetchone()[0], 1)
            self.assertEqual(conn.execute("select count(*) from copilot_messages where session_id=?", (first["session_id"],)).fetchone()[0], 4)
            latest = conn.execute("select context_json from copilot_messages where session_id=? and role='assistant' order by id desc limit 1", (first["session_id"],)).fetchone()
        context = json.loads(latest["context_json"])
        self.assertEqual(context["context"]["page_context"]["name"], "Osprey")
        self.assertEqual(context["context"]["conversation_context"]["session_id"], first["session_id"])

    def test_action_draft_requires_evidence_and_is_idempotent(self):
        answer, answer_code = self.app.create_copilot_answer(
            self.user,
            "今天企业最需要处理什么？",
            "",
            "",
            {"page": "/", "title": "老板经营大脑"},
        )
        self.assertEqual(answer_code, 200)
        with portal.db() as conn:
            message = conn.execute("select id from copilot_messages where id=? and role='assistant'", (answer["message_id"],)).fetchone()
        created, code = self.app.copilot_action_draft(self.user, message["id"])
        repeated, repeated_code = self.app.copilot_action_draft(self.user, message["id"])
        self.assertEqual(code, 200)
        self.assertEqual(repeated_code, 200)
        self.assertEqual(created["task_id"], repeated["task_id"])
        with portal.db() as conn:
            task = conn.execute("select * from tasks where id=?", (created["task_id"],)).fetchone()
        self.assertEqual(task["status"], "draft")
        self.assertEqual(task["source_type"], "copilot_message")

    def test_drive_upload_uses_current_extraction_schema(self):
        class Upload:
            filename = "upload-regression.txt"
            type = "text/plain"
            file = io.BytesIO(b"VAFOX upload regression test")

        class Form(dict):
            def getfirst(self, key, default=""):
                return self.get(key, default)

        self.app.headers = {"Content-Length": "35", "Accept": "application/json"}
        self.app.multipart = lambda: Form(file=Upload(), folder_id="")
        self.app.log_action = lambda *args, **kwargs: None
        self.app.process_document_to_knowledge = lambda *args, **kwargs: {"ok": True}
        self.app.json_out = lambda data, code=200: (data, code)

        result, code = self.app.api_drive_upload(self.user)

        self.assertEqual(code, 200)
        self.assertTrue(result["ok"])
        file_id = result["file"]["id"]
        with portal.db() as conn:
            extraction = conn.execute(
                "select text_content, created_at, updated_at from drive_file_extractions where file_id=?",
                (file_id,),
            ).fetchone()
        self.assertIn("VAFOX upload regression test", extraction["text_content"])
        self.assertEqual(extraction["created_at"], extraction["updated_at"])

    def test_baidu_drive_share_requires_official_https_url(self):
        old_url = os.environ.get("BAIDU_DRIVE_SHARE_URL")
        old_code = os.environ.get("BAIDU_DRIVE_SHARE_CODE")
        try:
            os.environ["BAIDU_DRIVE_SHARE_URL"] = "https://pan.baidu.com/s/test-share"
            os.environ["BAIDU_DRIVE_SHARE_CODE"] = "1102"
            self.assertEqual(portal.baidu_drive_share_url(), "https://pan.baidu.com/s/test-share?pwd=1102")
            os.environ["BAIDU_DRIVE_SHARE_URL"] = "https://example.com/s/test-share"
            self.assertEqual(portal.baidu_drive_share_url(), "")
        finally:
            if old_url is None:
                os.environ.pop("BAIDU_DRIVE_SHARE_URL", None)
            else:
                os.environ["BAIDU_DRIVE_SHARE_URL"] = old_url
            if old_code is None:
                os.environ.pop("BAIDU_DRIVE_SHARE_CODE", None)
            else:
                os.environ["BAIDU_DRIVE_SHARE_CODE"] = old_code

    def test_ceo_navigation_uses_five_product_entries(self):
        page = portal.layout("测试", "", user=self.user)
        for label, url in [("今天", "/"), ("企业", "/enterprise"), ("企业资料", "/drive"), ("AI助手", "/copilot"), ("系统", "/system")]:
            self.assertIn('href="{}">{}'.format(url, label), page)
        self.assertNotIn('class="primary-nav"><a href="/">首页', page)

    def test_profit_composition_never_adds_rebate_twice(self):
        profit = self.app.profit_composition_payload()
        self.assertAlmostEqual(profit["sap_profit"], 1723487.13, places=2)
        self.assertAlmostEqual(profit["rebate_total"], 1044717.78, places=2)
        self.assertAlmostEqual(profit["non_rebate_profit"], 678769.35, places=2)
        self.assertAlmostEqual(profit["osprey_rebate"] + profit["kailas_rebate"], profit["rebate_total"], places=2)

    def test_manual_report_publication_controls_freshness_without_claiming_auto_sync(self):
        now = int(time.time())
        with portal.db() as conn:
            conn.execute("delete from manual_business_report_publications")
            conn.execute(
                "insert into manual_business_report_publications(report_period_start,report_period_end,source_kind,source_reference,previous_snapshot_json,published_snapshot_json,reconciliation_json,approved_by,published_at) values(?,?,?,?,?,?,?,?,?)",
                ("2026-01-01", "2026-07-12", "sap_report_screenshot", "7.12.jpg", "[]", "{}", "{}", self.user["id"], now),
            )
        freshness = self.app.enterprise_sync_freshness_summary()
        self.assertEqual(freshness["status"], "manual_verified")
        self.assertIn("人工核对", freshness["message"])
        self.assertEqual(self.app.status_label(freshness["status"]), "人工核对已更新")

    def test_enterprise_and_system_pages_are_friendly(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.enterprise_center_page(self.user)
        self.app.system_center_page(self.user)
        combined = "\n".join(rendered)
        self.assertIn("企业数字档案", combined)
        self.assertIn("账号与管理", combined)
        self.assertNotIn("/api/", combined)
        self.assertNotIn("JSON", combined)

    def test_drive_copy_creates_independent_file(self):
        drive_dir = Path(TEST_APP_DIR) / "uploads" / "drive"
        drive_dir.mkdir(parents=True, exist_ok=True)
        source_path = drive_dir / "copy-source.txt"
        source_path.write_text("copy source", encoding="utf-8")
        now = int(time.time())
        with portal.db() as conn:
            root = conn.execute("select id from drive_folders where parent_id is null order by id limit 1").fetchone()
            cur = conn.execute(
                "insert into documents(title,file_name,file_type,file_path,uploaded_by,created_at,updated_at,filename,original_filename,storage_path,mime_type,extension,size_bytes,category,processing_status,version,created_by,drive_folder_id,content_hash,drive_visibility) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("copy-source.txt", "copy-source.txt", "txt", str(source_path), self.user["id"], now, now, "copy-source.txt", "copy-source.txt", str(source_path), "text/plain", "txt", source_path.stat().st_size, "其他资料", "indexed", 1, self.user["id"], root["id"], "copy-test-hash", "team"),
            )
            source_id = cur.lastrowid
        self.app.headers = {"Accept": "application/json"}
        self.app.form = lambda: {}
        self.app.log_action = lambda *args, **kwargs: None
        self.app.process_document_to_knowledge = lambda *args, **kwargs: {"ok": True}
        self.app.json_out = lambda data, code=200: (data, code)
        result, code = self.app.api_drive_post(self.user, "/api/drive/files/{}/copy".format(source_id))
        self.assertEqual(code, 200)
        self.assertNotEqual(result["id"], source_id)
        with portal.db() as conn:
            copied = conn.execute("select * from documents where id=?", (result["id"],)).fetchone()
        self.assertTrue(copied["original_filename"].startswith("副本 - "))
        self.assertNotEqual(copied["storage_path"], str(source_path))
        self.assertEqual(Path(copied["storage_path"]).read_text(encoding="utf-8"), "copy source")

    def test_today_page_has_genesis_ceo_structure(self):
        rendered = []
        self.app.path = "/"
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.dashboard(self.user)
        page = rendered[0]
        for text in ["企业健康", "今日经营", "今日风险", "今日机会", "今日建议", "今日行动", "CEO Vault"]:
            self.assertIn(text, page)
        self.assertNotIn("当前经营数字", page)
        self.assertNotIn("快速入口", page)
        self.assertNotIn("/api/", page)
        self.assertNotIn("Engine", page)

    def test_genesis_foundation_builds_stable_evidence_backed_relations(self):
        now = int(time.time())
        with portal.db() as conn:
            cur = conn.execute(
                "insert into enterprise_objects(object_type,code,name,status,description,tags,metadata,ai_summary,created_by,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?,?)",
                ("brand", "GENESIS-BRAND", "Genesis Test Brand", "active", "", "[]", "{}", "", self.user["id"], now, now),
            )
            object_id = cur.lastrowid
            root = conn.execute("select id from drive_folders where parent_id is null order by id limit 1").fetchone()
            cur = conn.execute(
                "insert into documents(title,file_name,file_type,file_path,uploaded_by,created_at,updated_at,filename,original_filename,storage_path,mime_type,extension,size_bytes,category,processing_status,version,created_by,drive_folder_id,content_hash,drive_visibility,related_object_type,related_object_id) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("Genesis evidence", "genesis.txt", "txt", "genesis.txt", self.user["id"], now, now, "genesis.txt", "genesis.txt", "genesis.txt", "text/plain", "txt", 1, "品牌资料", "indexed", 1, self.user["id"], root["id"], "genesis-evidence-hash", "team", "brand", object_id),
            )
            document_id = cur.lastrowid
        first = self.app.rebuild_enterprise_foundation(self.user)
        with portal.db() as conn:
            object_row = conn.execute("select * from enterprise_entity_registry where local_table='enterprise_objects' and local_id=?", (str(object_id),)).fetchone()
            document_row = conn.execute("select * from enterprise_entity_registry where local_table='documents' and local_id=?", (str(document_id),)).fetchone()
            relation = conn.execute("select * from enterprise_relationships where source_global_id=? and target_global_id=?", (document_row["global_id"], object_row["global_id"])).fetchone()
            count_before = conn.execute("select count(*) from enterprise_relationships").fetchone()[0]
        second = self.app.rebuild_enterprise_foundation(self.user)
        with portal.db() as conn:
            stable = conn.execute("select global_id from enterprise_entity_registry where local_table='enterprise_objects' and local_id=?", (str(object_id),)).fetchone()[0]
            count_after = conn.execute("select count(*) from enterprise_relationships").fetchone()[0]
            missing = conn.execute("select count(*) from enterprise_relationships where evidence_json is null or evidence_json='' or evidence_json='[]'").fetchone()[0]
        self.assertTrue(first["ok"])
        self.assertTrue(second["ok"])
        self.assertEqual(object_row["global_id"], stable)
        self.assertIsNotNone(relation)
        self.assertTrue(json.loads(relation["evidence_json"]))
        self.assertEqual(count_before, count_after)
        self.assertEqual(missing, 0)

    def test_genesis_pages_are_chinese_and_hide_technical_details(self):
        rendered = []
        self.app.path = "/ceo-memory"
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.enterprise_foundation_page(self.user)
        self.app.enterprise_dna_page(self.user)
        self.app.ceo_memory_page(self.user)
        combined = "\n".join(rendered)
        for text in ["企业基础", "企业 DNA", "企业时间机"]:
            self.assertIn(text, combined)
        for technical in ["enterprise_entity_registry", "enterprise_relationships", "JSON"]:
            self.assertNotIn(technical, combined)

    def test_drive_page_supports_batch_drag_and_progress(self):
        rendered = []
        self.app.path = "/drive"
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.drive_2_page(self.user)
        page = rendered[0]
        self.assertIn('type="file" multiple', page)
        self.assertIn("drive-drop-zone", page)
        self.assertIn("drive-upload-progress", page)
        self.assertIn("上传完成：成功", page)


    def test_ceo_vault_and_enterprise_network_render(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.ceo_vault_page(self.user)
        self.app.enterprise_network_page(self.user)
        self.assertEqual(len(rendered), 2)
        self.assertIn(portal.U(r"\u8001\u677f\u4fdd\u9669\u5e93"), rendered[0])
        self.assertIn(portal.U(r"\u4f01\u4e1a\u77e5\u8bc6\u7f51\u7edc"), rendered[1])

    def test_enterprise_brain_pages_render_in_chinese(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.enterprise_brain_page(self.user)
        self.app.enterprise_constitution_page(self.user)
        self.app.founder_memory_page(self.user)
        self.app.enterprise_brain_timeline_page(self.user)
        self.app.enterprise_asset_map_page(self.user)
        self.app.ceo_brain_decision_page(self.user)
        self.assertEqual(len(rendered), 6)
        combined = "\n".join(rendered)
        for text in ("CEO 企业大脑", "企业宪章", "创始人记忆", "企业时间轴", "企业资产地图", "CEO 决策中心"):
            self.assertIn(text, combined)
        for technical in ("enterprise_constitutions", "founder_memories", "decision_insights", "sync_runs"):
            self.assertNotIn(technical, combined)

    def test_ceo_operating_loop_pages_render_in_chinese(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.ceo_operating_loop_page(self.user)
        self.app.ceo_morning_brief_page(self.user)
        self.app.enterprise_question_center_page(self.user)
        self.app.decision_memory_loop_page(self.user)
        self.app.operating_evidence_chain_page(self.user)
        self.app.operating_review_page(self.user)
        self.assertEqual(len(rendered), 6)
        combined = "\n".join(rendered)
        for text in ("CEO 经营闭环", "CEO 早晨简报", "企业问题中心", "决策记忆", "依据链", "经营复盘"):
            self.assertIn(text, combined)
        for technical in ("ceo_morning_briefs", "enterprise_questions", "ceo_decision_memories", "operating_evidence_links"):
            self.assertNotIn(technical, combined)

    def test_proactive_signals_require_evidence(self):
        now = int(time.time())
        with portal.db() as conn:
            conn.execute("delete from proactive_signals")
            conn.execute("delete from decision_insights")
            conn.execute(
                "insert into decision_insights(insight_type,title,summary,severity,status,evidence,suggestion,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                ("risk", "evidence-backed", "verified", "high", "new", json.dumps([{"source": "test", "value": 1}]), "review", now, now),
            )
            conn.execute(
                "insert into decision_insights(insight_type,title,summary,severity,status,evidence,suggestion,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                ("risk", "unsupported", "must not publish", "high", "new", "[]", "ignore", now, now),
            )
        result = self.app.rebuild_proactive_signals(self.user)
        self.assertTrue(result["ok"])
        with portal.db() as conn:
            titles = [row["title"] for row in conn.execute("select title from proactive_signals").fetchall()]
        self.assertIn("evidence-backed", titles)
        self.assertNotIn("unsupported", titles)

    def test_decision_action_and_outcome_form_closed_loop(self):
        now = int(time.time())
        with portal.db() as conn:
            cur = conn.execute(
                "insert into decision_insights(insight_type,title,summary,severity,status,evidence,suggestion,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                ("risk", "closed-loop-test", "verified", "high", "accepted", json.dumps([{"source": "test"}]), "review stock", now, now),
            )
            insight_id = cur.lastrowid
            conn.execute(
                "insert into decision_evidence(insight_id,source_type,source_id,evidence_title,evidence_summary,confidence,created_at) values(?,?,?,?,?,?,?)",
                (insight_id, "test", "1", "test evidence", "verified", 0.9, now),
            )
        self.app.headers = {"Accept": "application/json"}
        self.app.json_out = lambda data, code=200: (data, code)
        self.app.api_object_payload = lambda: {"action_title": "review stock", "owner": "owner"}
        action, action_code = self.app.api_decision_post(self.user, "/api/decision/insights/{}/actions".format(insight_id))
        self.assertEqual(action_code, 200)
        self.assertTrue(action["ok"])
        self.app.api_object_payload = lambda: {"outcome_status": "effective", "result_summary": "sales improved", "actual_impact": "+10%", "evidence_note": "weekly sales report"}
        outcome, outcome_code = self.app.api_decision_post(self.user, "/api/decision/insights/{}/outcomes".format(insight_id))
        self.assertEqual(outcome_code, 200)
        self.assertTrue(outcome["ok"])
        with portal.db() as conn:
            task = conn.execute("select * from tasks where id=?", (action["task_id"],)).fetchone()
            saved = conn.execute("select * from decision_outcomes where id=?", (outcome["outcome_id"],)).fetchone()
        self.assertEqual(task["status"], "draft")
        self.assertEqual(saved["outcome_status"], "effective")
        self.assertTrue(json.loads(saved["evidence_json"]))

    def test_ceo_operating_workbench_and_object_center_are_business_friendly(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.ceo_operating_workbench_page(self.user)
        self.app.path = "/object-center"
        self.app.object_engine_page(self.user)
        combined = "\n".join(rendered)
        self.assertIn(portal.U(r"CEO \u7ecf\u8425\u5de5\u4f5c\u53f0"), combined)
        self.assertIn(portal.U(r"\u4f01\u4e1a\u5bf9\u8c61\u5de5\u4f5c\u53f0"), combined)
        self.assertNotIn("Everything is an Object", combined)
        self.assertNotIn("V1.1 Contract", combined)

    def test_v28_agent_run_is_evidence_first_and_review_gated(self):
        self.app.headers = {"Accept": "application/json"}
        self.app.form = lambda: {"agent_code": "business_analysis_agent", "question": "current business risks"}
        self.app.json_out = lambda data, code=200: (data, code)
        self.app.log_action = lambda *args, **kwargs: None
        payload, code = self.app.api_agents_post(self.user, "/api/agents/run")
        self.assertEqual(code, 200)
        self.assertTrue(payload["evidence"])
        self.assertTrue(payload["human_confirmation_required"])
        with portal.db() as conn:
            run = conn.execute("select * from ai_agent_runs where id=?", (payload["run_id"],)).fetchone()
        self.assertEqual(run["human_review_status"], "pending")
        self.assertTrue(json.loads(run["evidence_json"]))

    def test_agent_feedback_creates_pending_training_sample(self):
        now = int(time.time())
        with portal.db() as conn:
            agent = conn.execute("select id from ai_agents where code='business_analysis_agent'").fetchone()
            cur = conn.execute("insert into ai_agent_runs(agent_id,user_id,input,output,status,started_at,finished_at,evidence_json,human_review_status) values(?,?,?,?,?,?,?,?,?)", (agent["id"], self.user["id"], "test", "draft", "completed", now, now, json.dumps([{"source_type": "test", "source_id": "1"}]), "pending"))
            run_id = cur.lastrowid
        self.app.headers = {"Accept": "application/json"}
        self.app.form = lambda: {"feedback_type": "modified", "boss_decision": "revise", "correction": "use margin", "actual_result": "pending"}
        self.app.json_out = lambda data, code=200: (data, code)
        payload, code = self.app.api_agents_post(self.user, "/api/agents/runs/{}/feedback".format(run_id))
        self.assertEqual(code, 200)
        self.assertEqual(payload["learning_status"], "pending_review")
        with portal.db() as conn:
            sample = conn.execute("select * from enterprise_training_samples where id=?", (payload["training_sample_id"],)).fetchone()
        self.assertEqual(sample["approval_status"], "pending_review")

    def test_ceo_memory_training_requires_evidence(self):
        self.app.headers = {"Accept": "application/json"}
        self.app.json_out = lambda data, code=200: (data, code)
        self.app.form = lambda: {"title": "decision", "background": "context", "decision": "approved", "evidence_note": ""}
        blocked, blocked_code = self.app.api_knowledge_training_post(self.user, "/api/knowledge-training/ceo-memory")
        self.assertEqual(blocked_code, 400)
        self.app.form = lambda: {"title": "decision", "background": "context", "factors": "inventory", "decision": "approved", "evidence_note": "report 1", "actual_result": "", "future_reference": "review"}
        created, created_code = self.app.api_knowledge_training_post(self.user, "/api/knowledge-training/ceo-memory")
        self.assertEqual(created_code, 200)
        self.assertEqual(created["status"], "draft")
        with portal.db() as conn:
            sample = conn.execute("select * from enterprise_training_samples where id=?", (created["training_sample_id"],)).fetchone()
        self.assertEqual(sample["approval_status"], "pending_review")

    def test_v29_training_center_is_chinese_and_hides_technical_contracts(self):
        rendered = []
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.knowledge_training_center_page(self.user)
        page = rendered[0]
        self.assertIn(portal.U(r"\u4f01\u4e1a\u77e5\u8bc6\u8bad\u7ec3"), page)
        self.assertIn(portal.U(r"CEO \u51b3\u7b56\u8bb0\u5fc6"), page)
        self.assertNotIn("/api/", page.replace("action=\"/api/", "action=\""))


def tearDownModule():
    shutil.rmtree(TEST_APP_DIR, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

class UXV3AINativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        portal.init()
        now = int(time.time())
        with portal.db() as conn:
            existing = conn.execute("select * from users where email=?", ("uxv3@example.test",)).fetchone()
            if not existing:
                conn.execute(
                    "insert into users(email,name,phone,store,role,status,password_hash,created_at,updated_at) values(?,?,?,?,?,?,?,?,?)",
                    ("uxv3@example.test", "呼总", "", "总部", "admin", "approved", portal.hp("test-only-password"), now, now),
                )

    def setUp(self):
        self.app = object.__new__(portal.App)
        with portal.db() as conn:
            self.user = conn.execute("select * from users where email=?", ("uxv3@example.test",)).fetchone()

    def test_ai_router_selects_hidden_agents_without_user_selection(self):
        routed = self.app.ai_router_engine("南山店最近最需要关注什么？")
        self.assertEqual(routed["intent"], "store_question")
        self.assertIn("Store Agent", routed["agents"])
        self.assertEqual(routed["selection_mode"], "hidden_auto")
        profit = self.app.ai_router_engine("为什么利润下降？")
        self.assertEqual(profit["intent"], "finance_question")
        self.assertIn("Finance Agent", profit["agents"])

    def test_ai_answer_contains_v3_required_sections_and_router_context(self):
        answer, code = self.app.create_copilot_answer(self.user, "Osprey库存风险？", "", "", {"page": "/copilot", "title": "AI Native Workspace"})
        self.assertEqual(code, 200)
        for label in ["结论", "原因", "数据来源", "建议", "下一步行动"]:
            self.assertIn(label, answer["answer"])
        self.assertIn("Supply Chain Agent", answer["hidden_agents"])
        self.assertEqual(answer["ai_router"]["selection_mode"], "hidden_auto")

    def test_ai_workspace_v3_home_removes_manual_agent_configuration(self):
        rendered = []
        self.app.path = "/copilot"
        self.app.out = lambda html, code=200: rendered.append(html)
        self.app.enterprise_copilot_page(self.user)
        page = rendered[0]
        self.assertIn("Hello, 呼总", page)
        self.assertIn("今天想了解什么", page)
        self.assertIn("南山店最近经营情况怎么样", page)
        self.assertNotIn("Agent selection", page)
        self.assertNotIn("Object type", page)
        self.assertNotIn("Manual data source", page)
