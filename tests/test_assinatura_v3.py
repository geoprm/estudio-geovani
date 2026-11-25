"""Contratos da assinatura para cortes privados e públicos."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from arquivo_oculto.v2 import assinatura


class AssinaturaV3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.venv')
        self.root = Path(self.temp.name)
        self.corte = self.root / 'corte'
        self.corte.mkdir()
        self.saida = self.root / 'saida'
        self.manifesto = self.root / 'manifesto.json'
        self.manifesto.write_text(json.dumps({
            'episode_id': 'AO-IC-E01',
            'assinatura_abertura': {'gancho': 'Hoje eu vou contar uma história.'}
        }), encoding='utf-8')
        (self.corte / 'video_app.mp4').write_bytes(b'input-video')
        (self.corte / 'subtitles.srt').write_text(
            '1\n00:00:00,000 --> 00:00:01,000\nUma pista.\n', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def run_compositor(self, mode, publicavel=False, source_mode=None, rights='original_production'):
        source = {'modo': source_mode or mode, 'assets': [{'rights_status': rights}]}
        raw_source = json.dumps(source).encode('utf-8')
        (self.corte / 'sources.json').write_bytes(raw_source)
        timeline = {'episode_id': 'AO-IC-E01', 'modo': mode, 'planos': [{'privado': False}]}
        (self.corte / 'timeline.json').write_text(json.dumps(timeline), encoding='utf-8')
        qa = {'modo': mode, 'status': 'pass', 'publicavel': publicavel,
              'arquivos': {'video_app.mp4': {'sha256': hashlib.sha256(b'input-video').hexdigest()},
                           'sources.json': {'sha256': hashlib.sha256(raw_source).hexdigest()}}}
        (self.corte / 'qa.json').write_text(json.dumps(qa), encoding='utf-8')
        args = ['assinatura', str(self.manifesto), str(self.corte), str(self.saida)]
        lock = {'character': {'reference_image': 'reference.png'}, 'voice': {'voice_id': 'approved'}}

        def fake_run(command, **kwargs):
            if command[-1] == 'video_app.mp4':
                (Path(kwargs['cwd']) / 'video_app.mp4').write_bytes(b'joined-video')

        with (
            patch.object(sys, 'argv', args),
            patch.object(assinatura.perfil, 'carregar_lock', return_value=lock),
            patch.object(assinatura, 'criar_abertura', return_value=([(0, 1000, 'Olá, criancinhas...')], 30)),
            patch.object(assinatura.subprocess, 'run', side_effect=fake_run),
        ):
            assinatura.main()
        return json.loads((self.saida / 'assinatura.json').read_text(encoding='utf-8'))

    def test_private_cut_keeps_private_mode(self):
        result = self.run_compositor('private_preview')
        self.assertEqual(result['modo'], 'private_preview')
        self.assertFalse(result['publicavel'])

    def test_verified_public_cut_keeps_public_mode(self):
        result = self.run_compositor('public_release', publicavel=True)
        self.assertEqual(result['modo'], 'public_release')
        self.assertTrue(result['publicavel'])
        self.assertEqual(result['base_video_sha256'], hashlib.sha256(b'input-video').hexdigest())

    def test_public_cut_requires_public_qa(self):
        with self.assertRaises(SystemExit):
            self.run_compositor('public_release', publicavel=False)

    def test_private_source_cannot_be_promoted_by_signature(self):
        with self.assertRaises(SystemExit):
            self.run_compositor('public_release', publicavel=True, source_mode='private_preview')

    def test_private_rights_cannot_be_promoted_by_signature(self):
        with self.assertRaises(SystemExit):
            self.run_compositor('public_release', publicavel=True, rights='private_research')


if __name__ == '__main__':
    unittest.main()
