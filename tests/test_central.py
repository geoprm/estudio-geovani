"""Testes da Central do Estúdio. Rodam numa cópia temporária (config e app), com vídeos sintéticos do FFmpeg.

  python tests/test_central.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix='central_teste_')
shutil.copytree(os.path.join(REPO, 'config'), os.path.join(TMP, 'config'))
os.makedirs(os.path.join(TMP, 'app'))
shutil.copyfile(os.path.join(REPO, 'app', 'index.html'), os.path.join(TMP, 'app', 'index.html'))
os.makedirs(os.path.join(TMP, 'entrada'))
os.environ['ESTUDIO_CENTRAL'] = TMP
sys.path.insert(0, os.path.join(REPO, 'ferramentas'))

import app_docs  # noqa: E402
import comum  # noqa: E402
import estudio  # noqa: E402
import midia  # noqa: E402
import pacote  # noqa: E402
import skills  # noqa: E402


def gerar_video(caminho, dur=3, w=1080, h=1920, preto_inicio=0.0, tudo_preto=False):
    fonte = f'color=c=black:s={w}x{h}:r=30:d={dur}' if tudo_preto else f'testsrc2=size={w}x{h}:rate=30:duration={dur}'
    vf = f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='lt(t,{preto_inicio})'" if preto_inicio else 'null'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i', fonte, '-f', 'lavfi', '-i',
                    f'sine=frequency=440:sample_rate=48000:duration={dur}', '-vf', vf, '-af', 'volume=4',
                    '-c:v', 'libx264', '-threads', '2', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', caminho],
                   check=True)
    return caminho


def pacote_video(perfil='direitaxx', titulo='Teste de entrega', **extra):
    pasta = pacote.novo(perfil, 'video_pronto', titulo, 'codex', 'C:\\teste')
    gerar_video(os.path.join(pasta, 'video.mp4'))
    m = comum.ler_json(os.path.join(pasta, 'entrega.json'))
    m['arquivos'] = {'video': 'video.mp4'}
    m['post']['legenda'] = 'Legenda de teste'
    m['checagem'] = {'fatos': 'sem_fatos', 'direitos': 'liberado', 'pessoas_identificaveis': 'nenhuma', 'observacoes': ''}
    m.update(extra)
    comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
    return pasta, m


class Central(unittest.TestCase):
    def test_01_apelidos_de_perfil(self):
        self.assertEqual(comum.resolver_perfil('Arquivo Oculto'), 'arquivo')
        self.assertEqual(comum.resolver_perfil('@direitaxx'), 'direitaxx')
        self.assertEqual(comum.resolver_perfil('Dr. Geovani Miranda'), 'drgeovani')
        self.assertEqual(comum.resolver_perfil('princesa-melinda'), 'melinda')
        self.assertIsNone(comum.resolver_perfil('perfil-que-nao-existe'))

    def test_02_novo_sem_video_e_recusado(self):
        pasta = pacote.novo('drgeovani', 'video_pronto', 'Sem arquivo', 'chatgpt')
        _, rel, _ = pacote.validar(pasta)
        self.assertFalse(rel.ok)
        self.assertTrue(any('video' in e for e in rel.erros))
        shutil.rmtree(pasta)

    def test_03_fluxo_completo_video(self):
        pasta, m = pacote_video(titulo='Fluxo completo')
        eid = estudio.receber_um(pasta)
        self.assertIsNotNone(eid)
        est = comum.estado_atual()[eid]
        self.assertEqual(est['estado'], 'aguardando_upload')
        destino = os.path.join(TMP, est['caminho'])
        pa = comum.ler_json(os.path.join(destino, '_app', 'doc_app.json'))
        self.assertEqual(pa['colecao'], 'pedidos')
        self.assertEqual(pa['doc']['perfil'], 'direitaxx')
        self.assertEqual(pa['doc']['formato'], 'depoimento')
        self.assertEqual(pa['doc']['status'], 'pronto')
        self.assertLessEqual(os.path.getsize(os.path.join(destino, '_app', 'video_app.mp4')), comum.config_app()['limite_video_app_bytes'])
        self.assertTrue(os.path.exists(os.path.join(destino, '_app', 'capa.jpg')))
        self.assertTrue(os.path.exists(os.path.join(destino, 'qa_estudio.json')))
        self.assertIn('video.mp4', comum.ler_json(os.path.join(destino, 'recepcao.json'))['sha256'])
        _, faltam = app_docs.registrar_assets(destino, ['a=abc123'])
        self.assertEqual(faltam, ['capa'])
        estudio.main(['assets', eid, 'capa=def456'])
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'pronto_para_app')
        estudio.main(['publicado', eid])
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'no_app')

    def test_04_fato_sem_fonte_e_recusado(self):
        pasta, m = pacote_video(titulo='Fato sem fonte')
        m['checagem']['fatos'] = 'conferidos'
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        _, rel, _ = pacote.validar(pasta)
        self.assertTrue(any('fonte' in e for e in rel.erros))
        self.assertIsNone(estudio.receber_um(pasta))
        self.assertTrue(os.path.exists(os.path.join(pasta, '_RECEPCAO.md')))
        shutil.rmtree(pasta)

    def test_05_paciente_pendente_no_drgeovani(self):
        pasta, m = pacote_video('drgeovani', 'Paciente pendente')
        m['checagem']['pessoas_identificaveis'] = 'pendente'
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        _, rel, _ = pacote.validar(pasta)
        self.assertTrue(any('paciente' in e for e in rel.erros))
        shutil.rmtree(pasta)

    def test_06_ia_sem_rotulo(self):
        pasta, m = pacote_video('arquivo', 'IA sem rotulo')
        m['post']['rotulo_ia'] = False
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        _, rel, _ = pacote.validar(pasta)
        self.assertTrue(any('rotulo_ia' in e for e in rel.erros))
        shutil.rmtree(pasta)

    def test_07_direitos_pendentes_viram_previa_privada(self):
        pasta, m = pacote_video('arquivo', 'Direitos pendentes')
        m['checagem']['direitos'] = 'pendente'
        m['formato'] = 'investigacao_90'
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        eid = estudio.receber_um(pasta)
        destino = os.path.join(TMP, comum.estado_atual()[eid]['caminho'])
        doc = comum.ler_json(os.path.join(destino, '_app', 'doc_app.json'))['doc']
        self.assertTrue(doc['pautaTitulo'].startswith('PRÉVIA PRIVADA'))
        self.assertIn('Não publicar', doc['resultado']['nota'])
        self.assertEqual(doc['formato'], 'ia')
        self.assertEqual(doc['formatoAO'], 'investigacao_90')

    def test_08_zip_inseguro_e_zip_bom(self):
        ruim = os.path.join(TMP, 'entrada', 'ruim.zip')
        with zipfile.ZipFile(ruim, 'w') as z:
            z.writestr('../fora.txt', 'x')
        with self.assertRaises(ValueError):
            pacote.abrir_zip(ruim)
        os.remove(ruim)
        bom = os.path.join(TMP, 'entrada', 'do-chatgpt.zip')
        m = pacote.modelo('dr-geovani', 'orientacao', 'Tom das legendas', 'chatgpt')
        m['orientacoes'] = 'Legendas mais curtas.'
        m['arquivos'] = {'roteiro': 'orientacao.md'}
        with zipfile.ZipFile(bom, 'w') as z:
            z.writestr('pacote/entrega.json', json.dumps(m))
            z.writestr('pacote/orientacao.md', '# Tom das legendas\n\nDetalhe completo.\n')
        destino = pacote.abrir_zip(bom)
        self.assertTrue(os.path.exists(os.path.join(destino, 'entrega.json')))
        eid = estudio.receber_um(destino)
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'orientacao_registrada')
        with open(os.path.join(TMP, 'orientacoes', 'drgeovani.md'), encoding='utf-8') as f:
            texto = f.read()
        self.assertIn('Legendas mais curtas.', texto)
        self.assertIn('**Documento completo:** [orientacao.md](../entregas/drgeovani/', texto)

    def test_09_arquivos_soltos_viram_rascunho(self):
        gerar_video(os.path.join(TMP, 'entrada', 'meu_video.mp4'), dur=2)
        with open(os.path.join(TMP, 'entrada', 'recado.txt'), 'w', encoding='utf-8') as f:
            f.write('Postar amanhã cedo.')
        pasta = pacote.agrupar_soltos()
        m = comum.ler_json(os.path.join(pasta, 'entrega.json'))
        self.assertEqual(m['arquivos']['video'], 'meu_video.mp4')
        self.assertIn('Postar amanhã', m['orientacoes'])
        _, rel, _ = pacote.validar(pasta)
        self.assertFalse(rel.ok)
        shutil.rmtree(pasta)

    def test_10_qa_tecnico(self):
        d = tempfile.mkdtemp(dir=TMP)
        bom = midia.qa_tecnico(gerar_video(os.path.join(d, 'bom.mp4')))
        self.assertNotEqual(bom['status'], 'fail')
        preto = midia.qa_tecnico(gerar_video(os.path.join(d, 'preto_inicio.mp4'), dur=4, preto_inicio=1.5))
        self.assertFalse(next(c for c in preto['checks'] if c['check'] == 'preto_no_inicio')['ok'])
        todo = midia.qa_tecnico(gerar_video(os.path.join(d, 'todo_preto.mp4'), tudo_preto=True))
        self.assertEqual(todo['status'], 'fail')
        horiz = midia.qa_tecnico(gerar_video(os.path.join(d, 'horizontal.mp4'), w=1920, h=1080))
        self.assertFalse(next(c for c in horiz['checks'] if c['check'] == 'proporcao_9x16')['ok'])

    def test_11_versao_app_cabe_no_limite(self):
        d = tempfile.mkdtemp(dir=TMP)
        src = gerar_video(os.path.join(d, 'src.mp4'), dur=4)
        limite = 300_000
        out = midia.exportar_app(src, os.path.join(d, 'app.mp4'), limite=limite)
        self.assertLessEqual(out['bytes'], limite)
        self.assertEqual(out['video']['codec'], 'h264')
        self.assertTrue(midia.faststart(os.path.join(d, 'app.mp4')))

    def test_12_exportar_reenquadra_16x9_para_9x16(self):
        d = tempfile.mkdtemp(dir=TMP)
        src = gerar_video(os.path.join(d, 'h.mp4'), w=1280, h=720)
        out = midia.exportar(src, os.path.join(d, 'v.mp4'), 'reels', 'blur')
        self.assertEqual((out['video']['largura'], out['video']['altura']), (1080, 1920))

    def test_13_pauta(self):
        pasta = pacote.novo('direitaxx', 'pauta', 'Ponte do rio', 'claude-chat')
        m = comum.ler_json(os.path.join(pasta, 'entrega.json'))
        m['pauta'].update({'abertura_a': 'A ponte que nunca saiu do papel.', 'roteiro': [{'tempo': '0-3 s', 'fala': 'Gancho'}], 'nota': 4})
        m['checagem']['fatos'] = 'sem_fatos'
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        eid = estudio.receber_um(pasta)
        est = comum.estado_atual()[eid]
        self.assertEqual(est['estado'], 'pronto_para_app')
        doc = comum.ler_json(os.path.join(TMP, est['caminho'], '_app', 'doc_app.json'))
        self.assertEqual(doc['colecao'], 'pautas')
        self.assertEqual(doc['doc']['roteiro'][0]['fala'], 'Gancho')
        self.assertEqual(doc['doc']['aberturaA'], 'A ponte que nunca saiu do papel.')

    def test_14_pauta_arquivo_sem_cenas_fica_na_central(self):
        pasta = pacote.novo('arquivo', 'pauta', 'Caso sem cenas', 'codex')
        m = comum.ler_json(os.path.join(pasta, 'entrega.json'))
        m['pauta']['roteiro'] = [{'tempo': '0-3 s', 'fala': 'Olá, criancinhas...'}]
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        eid = estudio.receber_um(pasta)
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'na_central')

    def test_15_melinda_fica_na_central(self):
        pasta, m = pacote_video('melinda', 'Primeira historinha', gerado_por_ia=True)
        m = comum.ler_json(os.path.join(pasta, 'entrega.json'))
        m['post']['rotulo_ia'] = True
        comum.gravar_json(os.path.join(pasta, 'entrega.json'), m)
        eid = estudio.receber_um(pasta)
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'na_central')

    def test_17_app_depois(self):
        """Pouca memória: recebe sem a versão do app e gera depois com `app <id>`."""
        pasta, m = pacote_video('direitaxx', 'Versao do app adiada')
        eid = estudio.receber_um(pasta, app_depois=True)
        est = comum.estado_atual()[eid]
        self.assertEqual(est['estado'], 'aguardando_versao_app')
        destino = os.path.join(TMP, est['caminho'])
        self.assertFalse(os.path.exists(os.path.join(destino, '_app')))
        estudio.main(['app', eid])
        self.assertEqual(comum.estado_atual()[eid]['estado'], 'aguardando_upload')
        self.assertTrue(os.path.exists(os.path.join(destino, '_app', 'video_app.mp4')))
        self.assertTrue(os.path.exists(os.path.join(destino, '_app', 'doc_app.json')))

    def test_16_skills_do_repositorio(self):
        """As 16 skills do repositório real: frontmatter, links locais e espelho do Codex idêntico."""
        r = subprocess.run([sys.executable, '-c', 'import sys; sys.path.insert(0, "ferramentas"); import skills; '
                            'p = skills.verificar(); print(len(skills.listar())); print("\\n".join(p)); sys.exit(1 if p else 0)'],
                           cwd=REPO, capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'ESTUDIO_CENTRAL': REPO})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertGreaterEqual(int(r.stdout.split()[0]), 16)


if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
