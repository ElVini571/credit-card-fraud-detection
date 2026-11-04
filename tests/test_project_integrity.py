"""Testes leves de integridade dos resultados publicados.
Não desserializam arquivos .joblib nem executam treinamento.
"""
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8") as file:
        return json.load(file)


class ProjectIntegrityTests(unittest.TestCase):
    def test_expected_artifacts_exist(self):
        expected = [
            "app.py",
            "Dockerfile",
            "compose.yaml",
            "models/pipeline_fraudes.joblib",
            "data/raw/Base de Dados - Projeto Integrador (1).xlsx",
            "powerbi/Deteccao_Fraudes_UFMS.pbix",
            "reports/figures/01 - Panorama.png",
            "reports/figures/02 - Desempenho do Modelo.png",
            "reports/figures/simulador_streamlit.png",
        ]
        for name in expected:
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).is_file(), f"Arquivo ausente: {name}")

    def test_confusion_matrix_and_metrics(self):
        m = read_json("reports/metricas_modelo.json")
        tp = m["verdadeiros_positivos"]
        fp = m["falsos_positivos"]
        fn = m["falsos_negativos"]
        tn = m["verdadeiros_negativos"]
        total = tp + fp + fn + tn
        self.assertEqual(total, m["total_teste"])
        self.assertEqual(total, 4000)
        self.assertTrue(all(isinstance(v, int) and v >= 0 for v in (tp, fp, fn, tn)))
        self.assertTrue(math.isclose(m["acuracia"], (tp + tn) / total, abs_tol=1e-10))
        self.assertTrue(math.isclose(m["precisao"], tp / (tp + fp), abs_tol=1e-10))
        self.assertTrue(math.isclose(m["recall"], tp / (tp + fn), abs_tol=1e-10))
        f1 = 2 * tp / (2 * tp + fp + fn)
        self.assertTrue(math.isclose(m["f1_score"], f1, abs_tol=1e-10))
        self.assertGreaterEqual(m["average_precision"], 0)
        self.assertLessEqual(m["average_precision"], 1)

    def test_validation_threshold_selection(self):
        limiar = read_json("reports/limiar_selecionado.json")
        metrics = read_json("reports/metricas_modelo.json")
        self.assertGreaterEqual(limiar["limiar"], 0)
        self.assertLessEqual(limiar["limiar"], 1)
        self.assertAlmostEqual(limiar["limiar"], metrics["limiar"])
        self.assertEqual(limiar["criterio"], "maior F1 na validacao")
        for key in ("precisao_validacao", "recall_validacao", "f1_validacao"):
            self.assertGreaterEqual(limiar[key], 0)
            self.assertLessEqual(limiar[key], 1)

    def test_model_selection_metadata(self):
        escolha = read_json("reports/modelo_selecionado.json")
        self.assertEqual(escolha["modelo"], "Regressao Logistica")
        self.assertGreater(
            escolha["average_precision_validacao"],
            escolha["average_precision_baseline"],
        )


if __name__ == "__main__":
    unittest.main()
