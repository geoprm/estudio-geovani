"""Regressões da direção editorial do Arquivo Oculto. Rode na raiz do estúdio."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arquivo_oculto import editorial


class EditorialV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.perfil, cls.base = editorial.carregar_perfil()
        cls.temporada = editorial.carregar_temporada(cls.perfil, cls.base)

    def test_temporada_completa_com_material_de_direcao(self):
        self.assertEqual(len(self.temporada), 10)
        self.assertEqual(len(self.perfil['templates']), 6)
        for roteiro, _ in self.temporada:
            with self.subTest(roteiro=roteiro['episode_id']):
                self.assertEqual(roteiro['formato'], 'investigacao_90')
                self.assertTrue(any(b['classe_visual'] == 'personagem' for b in roteiro['beats']))
                palavras = sum(len(b['fala'].split()) for b in roteiro['beats'])
                self.assertGreaterEqual(palavras, 100)
                self.assertLessEqual(palavras, 160)

    def test_plano_documental_sem_fonte_e_reprovado(self):
        pasta = editorial.ESTUDIO / self.perfil['temporada']
        original = pasta / 'AO-S01-E02.v3.json'
        roteiro = editorial.ler_json(original)
        roteiro['manifesto_base'] = str((pasta / roteiro['manifesto_base']).resolve())
        beat = next(b for b in roteiro['beats'] if b['classe_visual'] == 'documental')
        beat['referencias'] = []
        with tempfile.TemporaryDirectory() as temporario:
            alterado = Path(temporario) / original.name
            alterado.write_text(json.dumps(roteiro), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'documental sem referência'):
                editorial.carregar_roteiro(alterado.parent, roteiro['episode_id'], self.base)

    def test_fabrica_bloqueia_roteiro_v3_antes_de_criar_saida(self):
        roteiro = editorial.ESTUDIO / self.perfil['temporada'] / 'AO-S01-E01.v3.json'
        with tempfile.TemporaryDirectory() as temporario:
            saida = Path(temporario) / 'saida'
            retorno = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'arquivo_oculto.v2.fabrica_v2',
                                      str(roteiro), '--saida', str(saida)], cwd=editorial.ESTUDIO,
                                     capture_output=True, text=True, encoding='utf-8', check=False)
            self.assertEqual(retorno.returncode, 2, retorno.stderr)
            self.assertIn('Roteiro editorial V3 em pré-produção', retorno.stderr)
            self.assertFalse(saida.exists())

    def test_consulta_retorna_template_registrado(self):
        resultado = subprocess.check_output([sys.executable, '-X', 'utf8', '-m', 'arquivo_oculto.editorial',
                                              '--template', 'youtube_5min'], cwd=editorial.ESTUDIO, encoding='utf-8')
        self.assertIn('16:9', resultado)
        self.assertIn('Capítulo 2', resultado)
        self.assertIn('Olá, criancinhas...', resultado)

    def test_caderno_corresponde_aos_roteiros(self):
        caderno = editorial.ESTUDIO / self.perfil['temporada'] / 'ROTEIROS_TEMPORADA_01.md'
        self.assertEqual(caderno.read_text(encoding='utf-8'), editorial.apresentar(self.temporada) + '\n')


if __name__ == '__main__':
    unittest.main()
