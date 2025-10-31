#!/usr/bin/env python3
"""
Conversor de XML S-5002 (e-Social) para PDF
Versão: 6.2.0
Gera comprovantes de rendimentos no formato oficial da Receita Federal
com TODOS os 33 grupos/subgrupos do e-Social S-1.3

Versão: 6.2.0
Data: 30/10/2025
Correções: Bug de paginação + Sistema de CSV auxiliar expandido
Novidades: Suporte para CSVs de dependentes e entidades + Paginação dinâmica ilimitada
Licença: MIT
"""

import xml.etree.ElementTree as ET
import argparse
import logging
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from decimal import Decimal

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FontePagadora:
    """Dados da fonte pagadora"""
    nome: str = ""
    cnpj: str = ""


@dataclass
class Beneficiario:
    """Dados do beneficiário"""
    cpf: str = ""
    nome: str = ""


@dataclass
class Dependente:
    """Dados de um dependente"""
    cpf: str = ""
    nome: str = ""
    dt_nascto: str = ""
    tp_dep: str = ""
    descr_dep: str = ""


@dataclass
class PensaoAlimenticia:
    """Dados de pensão alimentícia"""
    cpf_beneficiario: str = ""
    nome_beneficiario: str = ""
    valor_mensal: float = 0.0
    valor_13: float = 0.0
    valor_plr: float = 0.0


@dataclass
class PrevidenciaComplementar:
    """Dados de previdência complementar"""
    cnpj: str = ""
    nome_entidade: str = ""
    tp_prev: str = ""  # 1=PGBL, 2=FAPI, 3=Funpresp, 4=Outros
    valor: float = 0.0


@dataclass
class InfoDepSau:
    """Dependente de plano de saúde - REESTRUTURADO V5.2.0"""
    cpf_dep: str = ""
    nm_dep: str = ""
    dt_nasc_dep: str = ""
    vlr_plano: Decimal = Decimal('0.00')


@dataclass
class PlanoSaude:
    """Dados de plano de saúde"""
    cnpj_operadora: str = ""
    nome_operadora: str = ""
    registro_ans: str = ""
    valor_titular: float = 0.0
    dependentes: List[Tuple[str, str, float]] = field(default_factory=list)  # (CPF, Nome, Valor) - LEGADO
    info_dep_sau: List[InfoDepSau] = field(default_factory=list)  # NOVO V5.2.0


@dataclass
class DetReembTit:
    """Detalhamento de reembolso do titular - NOVO V5.2.0"""
    tp_insc: str = ""
    nr_insc: str = ""
    vlr_reemb: Decimal = Decimal('0.00')
    vlr_deducao: Decimal = Decimal('0.00')


@dataclass
class InfoReembDep:
    """Reembolso de dependente - NOVO V5.2.0"""
    cpf_dep: str = ""
    vlr_reemb: Decimal = Decimal('0.00')
    vlr_deducao: Decimal = Decimal('0.00')


@dataclass
class ReembolsoMedico:
    """Dados de reembolso médico"""
    cnpj_prestador: str = ""
    cpf_medico: str = ""
    nome_medico: str = ""
    valor_reembolsado: float = 0.0
    valor_reembolsado_anos_ant: float = 0.0
    valor_dedutivel: float = 0.0
    # NOVOS V5.2.0
    det_reemb_tit: Optional[DetReembTit] = None
    info_reemb_dep: List[InfoReembDep] = field(default_factory=list)


@dataclass
class IdeAdv:
    """Identificação de advogado - NOVO V5.2.0"""
    tp_insc: str = ""
    nr_insc: str = ""
    vlr_adv: Decimal = Decimal('0.00')
    nm_adv: str = ""  # NOVO V5.2.2


@dataclass
class DespProc:
    """Despesas com processo judicial - NOVO V5.2.0"""
    vlr_desp_proc: Decimal = Decimal('0.00')
    vlr_adv: Decimal = Decimal('0.00')
    ide_adv: List[IdeAdv] = field(default_factory=list)


@dataclass
class InfoRRA:
    """Rendimentos Recebidos Acumuladamente"""
    descricao: str = ""
    custas_judiciais: float = 0.0
    despesas_advogados: float = 0.0
    advogados: List[Tuple[str, str, float]] = field(default_factory=list)  # (CPF/CNPJ, Nome, Valor) - LEGADO
    # NOVO V5.2.0
    desp_proc: Optional[DespProc] = None


@dataclass
class EndExt:
    """Endereço no exterior - NOVO V5.2.0"""
    end_dsclograd: str = ""
    end_nrlograd: str = ""
    end_complem: str = ""
    end_bairro: str = ""
    end_nmcid: str = ""
    end_codpostal: str = ""


@dataclass
class PagamentoExterior:
    """Pagamento no Exterior"""
    pais: str = ""
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    cod_postal: str = ""
    # NOVO V5.2.0
    end_ext: Optional[EndExt] = None


# ============================================================================
# NOVOS GRUPOS DA V5.1.0 E V5.2.0
# ============================================================================

@dataclass
class TotInfoDmDev:
    """Totalização dos demonstrativos - NOVO V5.2.0"""
    vlr_tot_rend_trib: Decimal = Decimal('0.00')
    vlr_tot_rend_trib_13: Decimal = Decimal('0.00')
    vlr_tot_rend_mole_grave: Decimal = Decimal('0.00')
    vlr_tot_rend_mole_grave_13: Decimal = Decimal('0.00')
    vlr_tot_rend_isen_65: Decimal = Decimal('0.00')
    vlr_tot_rend_isen_65_13: Decimal = Decimal('0.00')
    vlr_tot_rend_trib_ant: Decimal = Decimal('0.00')
    vlr_tot_rend_trib_ant_13: Decimal = Decimal('0.00')
    vlr_tot_rend_trib_susp: Decimal = Decimal('0.00')
    vlr_tot_rend_trib_susp_13: Decimal = Decimal('0.00')

@dataclass
class BenefPen:
    """Beneficiário de dedução suspensa"""
    cpf_dep: str
    vlr_depen_susp: Decimal


@dataclass
class DedSusp:
    """Dedução com exigibilidade suspensa"""
    ind_tp_deducao: str
    descr_deducao: str
    vlr_ded_susp: Decimal
    cnpj_entid_pc: Optional[str] = None
    vlr_patroc_funp: Optional[Decimal] = None
    benef_pen: List[BenefPen] = field(default_factory=list)


@dataclass
class InfoValores:
    """Valores relacionados a processos"""
    ind_apuracao: str
    vlr_nao_retido: Decimal = Decimal('0.00')
    vlr_dep_judicial: Decimal = Decimal('0.00')
    vlr_comp_ano: Decimal = Decimal('0.00')
    vlr_comp_anos_ant: Decimal = Decimal('0.00')
    vlr_rend_susp: Decimal = Decimal('0.00')
    ded_susp: List[DedSusp] = field(default_factory=list)


@dataclass
class ProcessoJudicial:
    """Processo Judicial de Não Retenção"""
    tp_proc_ret: str = ""
    nr_proc_ret: str = ""
    cod_susp: str = ""
    info_valores: List[InfoValores] = field(default_factory=list)
    # Campos antigos para compatibilidade
    numero_processo: str = ""
    codigo_suspensao: str = ""
    valor_nao_retido: float = 0.0
    deposito_judicial: float = 0.0
    compensacao_ano: float = 0.0
    compensacao_anos_ant: float = 0.0
    rendimento_suspenso: float = 0.0


@dataclass
class DedDepen:
    """Dedução por dependente"""
    tp_rend: str
    cpf_dep: str
    vlr_ded_dep: Decimal


@dataclass
class InfoIRCR:
    """Informações de IR por Código de Receita"""
    tp_cr: str
    vr_cr: Decimal
    ded_depen: List[DedDepen] = field(default_factory=list)
    pen_alim: List[PensaoAlimenticia] = field(default_factory=list)
    previd_compl: List[PrevidenciaComplementar] = field(default_factory=list)
    info_proc_ret: List[ProcessoJudicial] = field(default_factory=list)


@dataclass
class PerAnt:
    """Informações de períodos anteriores"""
    info: str = "Ajustes de períodos anteriores"


@dataclass
class InfoProcJudRub:
    """Processo judicial aplicável a rubrica"""
    nr_proc: str
    uf_vara: str
    cod_munic: str
    id_vara: str


@dataclass
class TotApurDia:
    """Totalizador diário"""
    per_apur_dia: str
    cr_dia: str
    frm_tribut: str
    pais_resid_ext: Optional[str] = None
    vlr_rend_trib: Decimal = Decimal('0.00')
    vlr_irrf: Decimal = Decimal('0.00')


@dataclass
class ConsolidApurMen:
    """Consolidação mensal"""
    cr_men: str
    vlr_rend_trib: Decimal = Decimal('0.00')
    vlr_rend_trib13: Decimal = Decimal('0.00')
    vlr_irrf: Decimal = Decimal('0.00')
    vlr_irrf13: Decimal = Decimal('0.00')


@dataclass
class RendimentoTributavel:
    """Rendimentos tributáveis e deduções"""
    total_rendimentos: float = 0.0
    contrib_previdenciaria: float = 0.0
    contrib_prev_privada: float = 0.0
    pensao_alimenticia: float = 0.0
    imposto_retido: float = 0.0


@dataclass
class RendimentoIsento:
    """Rendimentos isentos e não tributáveis"""
    parcela_isenta_65: float = 0.0
    diarias: float = 0.0
    ajuda_custo: float = 0.0
    indenizacoes: float = 0.0
    abono_pecuniario: float = 0.0
    molestia_grave: float = 0.0
    outros: float = 0.0


@dataclass
class RendimentoExclusivo:
    """Rendimentos com tributação exclusiva"""
    decimo_terceiro: float = 0.0
    plr: float = 0.0
    rra: float = 0.0
    outros: float = 0.0


@dataclass
class ComprovanteRendimentos:
    """Comprovante completo de rendimentos"""
    ano: str
    fonte_pagadora: FontePagadora
    beneficiario: Beneficiario
    rendimento_tributavel: RendimentoTributavel
    rendimento_isento: RendimentoIsento
    rendimento_exclusivo: RendimentoExclusivo
    # Informações complementares
    dependentes: List[Dependente] = field(default_factory=list)
    pensoes_alimenticias: List[PensaoAlimenticia] = field(default_factory=list)
    previdencias_complementares: List[PrevidenciaComplementar] = field(default_factory=list)
    planos_saude: List[PlanoSaude] = field(default_factory=list)
    reembolsos_medicos: List[ReembolsoMedico] = field(default_factory=list)
    info_rra: Optional[InfoRRA] = None
    pagamento_exterior: Optional[PagamentoExterior] = None
    processos_judiciais: List[ProcessoJudicial] = field(default_factory=list)
    # NOVOS GRUPOS V5.1.0
    info_ir_cr: List[InfoIRCR] = field(default_factory=list)
    per_ant: Optional[PerAnt] = None
    info_proc_jud_rub: List[InfoProcJudRub] = field(default_factory=list)
    tot_apur_dia: List[TotApurDia] = field(default_factory=list)
    consolid_apur_men: List[ConsolidApurMen] = field(default_factory=list)
    # NOVO GRUPO V5.2.0
    tot_info_dm_dev: Optional[TotInfoDmDev] = None


class S5002Parser:
    """Parser de arquivos XML S-5002 do e-Social"""
    
    # Namespace do e-Social
    NS = {'esocial': 'http://www.esocial.gov.br/schema/evt/evtIrrfBenef/v_S_01_02_00'}
    
    # Mapeamento de códigos tpInfoIR para campos do comprovante
    CODIGO_IRRF = {
        # Rendimentos tributáveis
        '11': 'rend_trib_mensal',
        '12': 'rend_trib_13',
        '14': 'rend_trib_plr',
        # Retenções
        '31': 'retencao_mensal',
        '32': 'retencao_13',
        '34': 'retencao_plr',
        # Deduções
        '41': 'ded_prev_oficial_mensal',
        '42': 'ded_prev_oficial_13',
        '46': 'ded_prev_privada_mensal',
        '47': 'ded_prev_privada_13',
        '51': 'ded_pensao_mensal',
        '52': 'ded_pensao_13',
        '54': 'ded_pensao_plr',
        '61': 'ded_fapi_mensal',
        '62': 'ded_fapi_13',
        '63': 'ded_funpresp_mensal',
        '64': 'ded_funpresp_13',
        '67': 'ded_plano_saude',
        # Isentos
        '70': 'isento_65_mensal',
        '71': 'isento_65_13',
        '72': 'isento_diarias',
        '73': 'isento_ajuda_custo',
        '74': 'isento_indenizacao',
        '75': 'isento_abono_pecuniario',
        '76': 'isento_molestia_mensal',
        '77': 'isento_molestia_13',
        '79': 'isento_outros',
        # RRA
        '7952': 'rra_tributavel',
        '7953': 'rra_retencao',
        '7954': 'rra_prev_oficial',
        '7955': 'rra_pensao',
    }
    
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = None
        self.root = None
    
    def parse(self) -> List[ComprovanteRendimentos]:
        """Parse do arquivo XML e retorna lista de comprovantes"""
        try:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
            
            comprovantes = []
            
            # Buscar todos os trabalhadores no arquivo
            for ide_trab in self.root.findall('.//esocial:ideTrabalhador', self.NS):
                comprovante = self._parse_trabalhador(ide_trab)
                if comprovante:
                    comprovantes.append(comprovante)
            
            return comprovantes
            
        except ET.ParseError as e:
            logger.error(f"Erro ao fazer parse do XML {self.xml_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao processar {self.xml_path}: {e}")
            raise
    
    def _parse_trabalhador(self, ide_trab) -> Optional[ComprovanteRendimentos]:
        """Parse dos dados de um trabalhador"""
        try:
            # Extrair ano de referência
            per_apur = self.root.find('.//esocial:perApur', self.NS)
            ano = per_apur.text[:4] if per_apur is not None else datetime.now().year
            
            # Dados do beneficiário
            cpf_benef = ide_trab.find('esocial:cpfBenef', self.NS)
            beneficiario = Beneficiario(
                cpf=cpf_benef.text if cpf_benef is not None else ""
            )
            
            # Dados da fonte pagadora (do ideEmpregador)
            fonte_pagadora = FontePagadora()
            ide_empregador = self.root.find('.//esocial:ideEmpregador', self.NS)
            if ide_empregador is not None:
                nr_insc = ide_empregador.find('esocial:nrInsc', self.NS)
                if nr_insc is not None:
                    fonte_pagadora.cnpj = nr_insc.text
            
            # Inicializar estruturas de dados
            valores = {}
            
            # Processar todos os dmDev
            for dm_dev in ide_trab.findall('esocial:dmDev', self.NS):
                # Processar infoIR
                for info_ir in dm_dev.findall('esocial:infoIR', self.NS):
                    tp_info = info_ir.find('esocial:tpInfoIR', self.NS)
                    valor = info_ir.find('esocial:valor', self.NS)
                    
                    if tp_info is not None and valor is not None:
                        codigo = tp_info.text
                        val = float(valor.text)
                        
                        if codigo in valores:
                            valores[codigo] += val
                        else:
                            valores[codigo] = val
            
            # Montar rendimentos tributáveis
            rend_trib = RendimentoTributavel(
                total_rendimentos=valores.get('11', 0.0) + valores.get('12', 0.0),
                contrib_previdenciaria=valores.get('41', 0.0) + valores.get('42', 0.0),
                contrib_prev_privada=(valores.get('46', 0.0) + valores.get('47', 0.0) + 
                                     valores.get('61', 0.0) + valores.get('62', 0.0) +
                                     valores.get('63', 0.0) + valores.get('64', 0.0)),
                pensao_alimenticia=valores.get('51', 0.0) + valores.get('52', 0.0) + valores.get('54', 0.0),
                imposto_retido=valores.get('31', 0.0) + valores.get('32', 0.0) + valores.get('34', 0.0)
            )
            
            # Montar rendimentos isentos
            rend_isento = RendimentoIsento(
                parcela_isenta_65=valores.get('70', 0.0) + valores.get('71', 0.0),
                diarias=valores.get('72', 0.0),
                ajuda_custo=valores.get('73', 0.0),
                indenizacoes=valores.get('74', 0.0),
                abono_pecuniario=valores.get('75', 0.0),
                molestia_grave=valores.get('76', 0.0) + valores.get('77', 0.0),
                outros=valores.get('79', 0.0)
            )
            
            # Montar rendimentos exclusivos
            rend_exclusivo = RendimentoExclusivo(
                decimo_terceiro=valores.get('12', 0.0),
                plr=valores.get('14', 0.0),
                rra=valores.get('7952', 0.0),
                outros=0.0
            )
            
            # Parse de informações complementares
            info_ir_complem = ide_trab.find('esocial:infoIRComplem', self.NS)
            dependentes = []
            pensoes = []
            previdencias = []
            planos_saude = []
            reembolsos = []
            
            if info_ir_complem is not None:
                # Dependentes
                for ide_dep in info_ir_complem.findall('esocial:ideDep', self.NS):
                    dep = self._parse_dependente(ide_dep)
                    if dep:
                        dependentes.append(dep)
                
                # Processar infoIRCR para pensões e previdências
                for info_ir_cr in info_ir_complem.findall('esocial:infoIRCR', self.NS):
                    # Pensões alimentícias
                    for pen_alim in info_ir_cr.findall('esocial:penAlim', self.NS):
                        pensao = self._parse_pensao(pen_alim)
                        if pensao:
                            pensoes.append(pensao)
                    
                    # Previdência complementar
                    for prev_compl in info_ir_cr.findall('esocial:previdCompl', self.NS):
                        prev = self._parse_previdencia(prev_compl)
                        if prev:
                            previdencias.append(prev)
                
                # Planos de saúde
                for plan_saude in info_ir_complem.findall('esocial:planSaude', self.NS):
                    plano = self._parse_plano_saude(plan_saude)
                    if plano:
                        planos_saude.append(plano)
                
                # Reembolsos médicos
                for info_reemb in info_ir_complem.findall('esocial:infoReembMed', self.NS):
                    reemb = self._parse_reembolso(info_reemb)
                    if reemb:
                        reembolsos.append(reemb)
            
            # Parse dos 3 novos grupos (v5.0.0)
            info_rra = None
            pagamento_exterior = None
            processos_judiciais = []
            
            # Parse dos 8 novos grupos (v5.1.0)
            info_ir_cr_list = []
            per_ant = None
            info_proc_jud_rub_list = []
            tot_apur_dia_list = []
            consolid_apur_men_list = []
            
            if info_ir_complem is not None:
                # Info RRA
                info_rra_elem = info_ir_complem.find('esocial:infoRRA', self.NS)
                if info_rra_elem is not None:
                    info_rra = self._parse_info_rra(info_rra_elem)
                
                # Pagamento no Exterior
                pgto_ext_elem = info_ir_complem.find('esocial:infoPgtoExt', self.NS)
                if pgto_ext_elem is not None:
                    pagamento_exterior = self._parse_pagamento_exterior(pgto_ext_elem)
                
                # Processos Judiciais
                for proc_elem in info_ir_complem.findall('esocial:infoProcRet', self.NS):
                    proc = self._parse_processo_judicial(proc_elem)
                    if proc:
                        processos_judiciais.append(proc)
                
                # ============ NOVOS GRUPOS V5.1.0 ============
                
                # InfoIRCR
                for info_cr_elem in info_ir_complem.findall('esocial:infoIRCR', self.NS):
                    info_cr = self._parse_info_ir_cr(info_cr_elem)
                    if info_cr:
                        info_ir_cr_list.append(info_cr)
                
                # PerAnt
                per_ant_elem = info_ir_complem.find('esocial:perAnt', self.NS)
                if per_ant_elem is not None:
                    per_ant = PerAnt()
                
                # InfoProcJudRub
                for proc_rub_elem in info_ir_complem.findall('esocial:infoProcJudRub', self.NS):
                    proc_rub = self._parse_info_proc_jud_rub(proc_rub_elem)
                    if proc_rub:
                        info_proc_jud_rub_list.append(proc_rub)
            
            # TotApurDia e ConsolidApurMen (podem estar em totInfoPerAnt)
            tot_info_per_ant = ide_trab.find('esocial:totInfoPerAnt', self.NS)
            if tot_info_per_ant is not None:
                # TotApurDia
                for tot_dia_elem in tot_info_per_ant.findall('esocial:totApurDia', self.NS):
                    tot_dia = self._parse_tot_apur_dia(tot_dia_elem)
                    if tot_dia:
                        tot_apur_dia_list.append(tot_dia)
                
                # ConsolidApurMen
                for cons_elem in tot_info_per_ant.findall('esocial:consolidApurMen', self.NS):
                    cons = self._parse_consolid_apur_men(cons_elem)
                    if cons:
                        consolid_apur_men_list.append(cons)
            
            # ============ NOVO GRUPO V5.2.0 ============
            # TotInfoDmDev - Totalização dos demonstrativos
            tot_info_dm_dev = None
            tot_info_dm_dev_elem = ide_trab.find('esocial:totInfoDmDev', self.NS)
            if tot_info_dm_dev_elem is not None:
                tot_info_dm_dev = self._parse_tot_info_dm_dev(tot_info_dm_dev_elem)
            
            # Criar comprovante
            comprovante = ComprovanteRendimentos(
                ano=str(ano),
                fonte_pagadora=fonte_pagadora,
                beneficiario=beneficiario,
                rendimento_tributavel=rend_trib,
                rendimento_isento=rend_isento,
                rendimento_exclusivo=rend_exclusivo,
                dependentes=dependentes,
                pensoes_alimenticias=pensoes,
                previdencias_complementares=previdencias,
                planos_saude=planos_saude,
                reembolsos_medicos=reembolsos,
                info_rra=info_rra,
                pagamento_exterior=pagamento_exterior,
                processos_judiciais=processos_judiciais,
                # NOVOS GRUPOS V5.1.0
                info_ir_cr=info_ir_cr_list,
                per_ant=per_ant,
                info_proc_jud_rub=info_proc_jud_rub_list,
                tot_apur_dia=tot_apur_dia_list,
                consolid_apur_men=consolid_apur_men_list,
                # NOVO GRUPO V5.2.0
                tot_info_dm_dev=tot_info_dm_dev
            )
            
            return comprovante
            
        except Exception as e:
            logger.error(f"Erro ao processar trabalhador: {e}")
            return None
    
    def _parse_dependente(self, ide_dep) -> Optional[Dependente]:
        """Parse de um dependente"""
        try:
            cpf = ide_dep.find('esocial:cpfDep', self.NS)
            nome = ide_dep.find('esocial:nmDep', self.NS)
            dt_nascto = ide_dep.find('esocial:dtNascto', self.NS)
            tp_dep = ide_dep.find('esocial:tpDep', self.NS)
            descr_dep = ide_dep.find('esocial:descrDep', self.NS)
            
            return Dependente(
                cpf=cpf.text if cpf is not None else "",
                nome=nome.text if nome is not None else "",
                dt_nascto=dt_nascto.text if dt_nascto is not None else "",
                tp_dep=tp_dep.text if tp_dep is not None else "",
                descr_dep=descr_dep.text if descr_dep is not None else ""
            )
        except Exception as e:
            logger.warning(f"Erro ao parse dependente: {e}")
            return None
    
    def _parse_pensao(self, pen_alim) -> Optional[PensaoAlimenticia]:
        """Parse de pensão alimentícia"""
        try:
            cpf = pen_alim.find('esocial:cpfDep', self.NS)
            valor = pen_alim.find('esocial:vlrPensao', self.NS)
            tp_rend = pen_alim.find('esocial:tpRend', self.NS)
            
            if cpf is not None and valor is not None:
                val = float(valor.text)
                tp = tp_rend.text if tp_rend is not None else '11'
                
                pensao = PensaoAlimenticia(cpf_beneficiario=cpf.text)
                
                if tp == '11':  # Mensal
                    pensao.valor_mensal = val
                elif tp == '12':  # 13º
                    pensao.valor_13 = val
                elif tp == '14':  # PLR
                    pensao.valor_plr = val
                
                return pensao
        except Exception as e:
            logger.warning(f"Erro ao parse pensão: {e}")
            return None
    
    def _parse_previdencia(self, prev_compl) -> Optional[PrevidenciaComplementar]:
        """Parse de previdência complementar"""
        try:
            cnpj = prev_compl.find('esocial:cnpjEntidPC', self.NS)
            tp_prev = prev_compl.find('esocial:tpPrev', self.NS)
            valor = prev_compl.find('esocial:vlrDeduzir', self.NS)
            
            if cnpj is not None:
                return PrevidenciaComplementar(
                    cnpj=cnpj.text,
                    tp_prev=tp_prev.text if tp_prev is not None else "",
                    valor=float(valor.text) if valor is not None else 0.0
                )
        except Exception as e:
            logger.warning(f"Erro ao parse previdência: {e}")
            return None
    
    def _parse_plano_saude(self, plan_saude) -> Optional[PlanoSaude]:
        """Parse de plano de saúde"""
        try:
            cnpj = plan_saude.find('esocial:cnpjOper', self.NS)
            nome = plan_saude.find('esocial:nmRazao', self.NS)
            reg_ans = plan_saude.find('esocial:regANS', self.NS)
            valor_tit = plan_saude.find('esocial:vlrSaudeTit', self.NS)
            
            plano = PlanoSaude(
                cnpj_operadora=cnpj.text if cnpj is not None else "",
                nome_operadora=nome.text if nome is not None else "",
                registro_ans=reg_ans.text if reg_ans is not None else "",
                valor_titular=float(valor_tit.text) if valor_tit is not None else 0.0
            )
            
            # Dependentes do plano (LEGADO - mantém compatibilidade)
            for info_dep in plan_saude.findall('esocial:infoDepSau', self.NS):
                cpf_dep = info_dep.find('esocial:cpfDep', self.NS)
                nome_dep = info_dep.find('esocial:nmDep', self.NS)
                dt_nasc_dep = info_dep.find('esocial:dtNascto', self.NS)
                valor_dep = info_dep.find('esocial:vlrSaudeDep', self.NS)
                
                if cpf_dep is not None:
                    # LEGADO
                    plano.dependentes.append((
                        cpf_dep.text,
                        nome_dep.text if nome_dep is not None else "",
                        float(valor_dep.text) if valor_dep is not None else 0.0
                    ))
                    # NOVO V5.2.0 - estrutura completa
                    plano.info_dep_sau.append(InfoDepSau(
                        cpf_dep=cpf_dep.text,
                        nm_dep=nome_dep.text if nome_dep is not None else "",
                        dt_nasc_dep=dt_nasc_dep.text if dt_nasc_dep is not None else "",
                        vlr_plano=Decimal(valor_dep.text) if valor_dep is not None else Decimal('0.00')
                    ))
            
            return plano
        except Exception as e:
            logger.warning(f"Erro ao parse plano saúde: {e}")
            return None
    
    def _parse_reembolso(self, info_reemb) -> Optional[ReembolsoMedico]:
        """Parse de reembolso médico"""
        try:
            reemb = ReembolsoMedico()
            
            # Reembolso do titular (LEGADO + NOVO V5.2.0)
            for det_reemb in info_reemb.findall('esocial:detReembTit', self.NS):
                tp_insc = det_reemb.find('esocial:tpInsc', self.NS)
                nr_insc = det_reemb.find('esocial:nrInsc', self.NS)
                valor_reemb = det_reemb.find('esocial:vlrReemb', self.NS)
                valor_ded = det_reemb.find('esocial:vlrDeduzir', self.NS)
                
                if nr_insc is not None:
                    # LEGADO
                    reemb.cnpj_prestador = nr_insc.text
                    reemb.valor_reembolsado = float(valor_reemb.text) if valor_reemb is not None else 0.0
                    reemb.valor_dedutivel = float(valor_ded.text) if valor_ded is not None else 0.0
                    # NOVO V5.2.0
                    reemb.det_reemb_tit = DetReembTit(
                        tp_insc=tp_insc.text if tp_insc is not None else "",
                        nr_insc=nr_insc.text,
                        vlr_reemb=Decimal(valor_reemb.text) if valor_reemb is not None else Decimal('0.00'),
                        vlr_deducao=Decimal(valor_ded.text) if valor_ded is not None else Decimal('0.00')
                    )
            
            # Reembolso de dependentes - NOVO V5.2.0
            for info_reemb_dep in info_reemb.findall('esocial:infoReembDep', self.NS):
                cpf_dep = info_reemb_dep.find('esocial:cpfDep', self.NS)
                valor_reemb = info_reemb_dep.find('esocial:vlrReemb', self.NS)
                valor_ded = info_reemb_dep.find('esocial:vlrDeduzir', self.NS)
                
                if cpf_dep is not None:
                    reemb.info_reemb_dep.append(InfoReembDep(
                        cpf_dep=cpf_dep.text,
                        vlr_reemb=Decimal(valor_reemb.text) if valor_reemb is not None else Decimal('0.00'),
                        vlr_deducao=Decimal(valor_ded.text) if valor_ded is not None else Decimal('0.00')
                    ))
            
            return reemb if reemb.cnpj_prestador else None
        except Exception as e:
            logger.warning(f"Erro ao parse reembolso: {e}")
            return None
    
    def _parse_info_rra(self, info_rra_elem) -> Optional[InfoRRA]:
        """Parse de informações de RRA"""
        try:
            descr = info_rra_elem.find('esocial:descrRRA', self.NS)
            
            info_rra = InfoRRA(
                descricao=descr.text if descr is not None else ""
            )
            
            # Despesas com processo judicial
            desp_proc_elem = info_rra_elem.find('esocial:despProcJud', self.NS)
            if desp_proc_elem is not None:
                # Tentar tag oficial primeiro, depois fallback para alias
                vlr_custas = desp_proc_elem.find('esocial:vlrDespCustas', self.NS)
                if vlr_custas is None:
                    vlr_custas = desp_proc_elem.find('esocial:vlrCustas', self.NS)  # Fallback
                    if vlr_custas is not None:
                        logger.warning("Tag 'vlrCustas' é um alias. Use 'vlrDespCustas' (oficial)")
                
                vlr_adv_total = desp_proc_elem.find('esocial:vlrDespAdvogados', self.NS)
                if vlr_adv_total is None:
                    vlr_adv_total = desp_proc_elem.find('esocial:vlrAdvogados', self.NS)  # Fallback
                    if vlr_adv_total is not None:
                        logger.warning("Tag 'vlrAdvogados' é um alias. Use 'vlrDespAdvogados' (oficial)")
                
                # LEGADO
                info_rra.custas_judiciais = float(vlr_custas.text) if vlr_custas is not None else 0.0
                info_rra.despesas_advogados = float(vlr_adv_total.text) if vlr_adv_total is not None else 0.0
                
                # NOVO V5.2.0 - Estrutura DespProc
                desp_proc = DespProc(
                    vlr_desp_proc=Decimal(vlr_custas.text) if vlr_custas is not None else Decimal('0.00'),
                    vlr_adv=Decimal(vlr_adv_total.text) if vlr_adv_total is not None else Decimal('0.00')
                )
                
                # Advogados
                for ide_adv_elem in desp_proc_elem.findall('esocial:ideAdv', self.NS):
                    tp_insc = ide_adv_elem.find('esocial:tpInsc', self.NS)
                    nr_insc = ide_adv_elem.find('esocial:nrInsc', self.NS)
                    valor = ide_adv_elem.find('esocial:vlrAdv', self.NS)
                    nm_adv = ide_adv_elem.find('esocial:nmAdv', self.NS)  # NOVO V5.2.2
                    
                    if nr_insc is not None:
                        nome_adv = nm_adv.text if nm_adv is not None else ""
                        # LEGADO
                        info_rra.advogados.append((
                            nr_insc.text,
                            nome_adv,
                            float(valor.text) if valor is not None else 0.0
                        ))
                        # NOVO V5.2.0
                        desp_proc.ide_adv.append(IdeAdv(
                            tp_insc=tp_insc.text if tp_insc is not None else "",
                            nr_insc=nr_insc.text,
                            vlr_adv=Decimal(valor.text) if valor is not None else Decimal('0.00'),
                            nm_adv=nome_adv
                        ))
                
                info_rra.desp_proc = desp_proc
            
            return info_rra
        except Exception as e:
            logger.warning(f"Erro ao parse info RRA: {e}")
            return None
    
    def _parse_pagamento_exterior(self, pgto_ext_elem) -> Optional[PagamentoExterior]:
        """Parse de pagamento no exterior"""
        try:
            pais = pgto_ext_elem.find('esocial:paisResidExt', self.NS)
            
            pgto_ext = PagamentoExterior(
                pais=pais.text if pais is not None else ""
            )
            
            # Endereço
            end_ext_elem = pgto_ext_elem.find('esocial:endExt', self.NS)
            if end_ext_elem is not None:
                logr = end_ext_elem.find('esocial:endDscLograd', self.NS)
                num = end_ext_elem.find('esocial:endNrLograd', self.NS)
                compl = end_ext_elem.find('esocial:endComplem', self.NS)
                bairro = end_ext_elem.find('esocial:endBairro', self.NS)
                cidade = end_ext_elem.find('esocial:endCidade', self.NS)
                cod_post = end_ext_elem.find('esocial:endCodPostal', self.NS)
                
                # LEGADO
                pgto_ext.logradouro = logr.text if logr is not None else ""
                pgto_ext.numero = num.text if num is not None else ""
                pgto_ext.complemento = compl.text if compl is not None else ""
                pgto_ext.bairro = bairro.text if bairro is not None else ""
                pgto_ext.cidade = cidade.text if cidade is not None else ""
                pgto_ext.cod_postal = cod_post.text if cod_post is not None else ""
                
                # NOVO V5.2.0
                pgto_ext.end_ext = EndExt(
                    end_dsclograd=logr.text if logr is not None else "",
                    end_nrlograd=num.text if num is not None else "",
                    end_complem=compl.text if compl is not None else "",
                    end_bairro=bairro.text if bairro is not None else "",
                    end_nmcid=cidade.text if cidade is not None else "",
                    end_codpostal=cod_post.text if cod_post is not None else ""
                )
            
            return pgto_ext
        except Exception as e:
            logger.warning(f"Erro ao parse pagamento exterior: {e}")
            return None
    
    def _parse_processo_judicial(self, proc_elem) -> Optional[ProcessoJudicial]:
        """Parse de processo judicial"""
        try:
            nr_proc = proc_elem.find('esocial:nrProc', self.NS)
            cod_susp = proc_elem.find('esocial:codSusp', self.NS)
            vlr_nao_ret = proc_elem.find('esocial:vlrNRetido', self.NS)
            vlr_dep = proc_elem.find('esocial:vlrDepJud', self.NS)
            vlr_comp_ano = proc_elem.find('esocial:vlrCompAnoCalend', self.NS)
            vlr_comp_ant = proc_elem.find('esocial:vlrCompAnoAnt', self.NS)
            vlr_rend_susp = proc_elem.find('esocial:vlrRendSusp', self.NS)
            
            return ProcessoJudicial(
                numero_processo=nr_proc.text if nr_proc is not None else "",
                codigo_suspensao=cod_susp.text if cod_susp is not None else "",
                valor_nao_retido=float(vlr_nao_ret.text) if vlr_nao_ret is not None else 0.0,
                deposito_judicial=float(vlr_dep.text) if vlr_dep is not None else 0.0,
                compensacao_ano=float(vlr_comp_ano.text) if vlr_comp_ano is not None else 0.0,
                compensacao_anos_ant=float(vlr_comp_ant.text) if vlr_comp_ant is not None else 0.0,
                rendimento_suspenso=float(vlr_rend_susp.text) if vlr_rend_susp is not None else 0.0
            )
        except Exception as e:
            logger.warning(f"Erro ao parse processo judicial: {e}")
            return None
    
    # ========================================================================
    # NOVOS PARSERS V5.1.0
    # ========================================================================
    
    def _parse_benef_pen(self, benef_elem) -> Optional[BenefPen]:
        """Parse de beneficiário de dedução suspensa"""
        try:
            cpf = benef_elem.find('esocial:cpfDep', self.NS)
            vlr = benef_elem.find('esocial:vlrDepenSusp', self.NS)
            
            return BenefPen(
                cpf_dep=cpf.text if cpf is not None else "",
                vlr_depen_susp=Decimal(vlr.text) if vlr is not None else Decimal('0.00')
            )
        except Exception as e:
            logger.warning(f"Erro ao parse beneficiário: {e}")
            return None
    
    def _parse_ded_susp(self, ded_elem) -> Optional[DedSusp]:
        """Parse de dedução suspensa"""
        try:
            ind_tp = ded_elem.find('esocial:indTpDeducao', self.NS)
            vlr_ded = ded_elem.find('esocial:vlrDedSusp', self.NS)
            cnpj = ded_elem.find('esocial:cnpjEntidPC', self.NS)
            vlr_patroc = ded_elem.find('esocial:vlrPatrocFunp', self.NS)
            
            # Parse beneficiários
            beneficiarios = []
            for benef in ded_elem.findall('esocial:benefPen', self.NS):
                b = self._parse_benef_pen(benef)
                if b:
                    beneficiarios.append(b)
            
            tipos_deducao = {
                '1': 'Previdência Oficial',
                '2': 'Previdência Privada',
                '3': 'FAPI',
                '4': 'Funpresp',
                '5': 'Dependente',
                '6': 'Plano de Saúde',
                '7': 'Pensão Alimentícia'
            }
            
            tp_ded = ind_tp.text if ind_tp is not None else ""
            
            return DedSusp(
                ind_tp_deducao=tp_ded,
                descr_deducao=tipos_deducao.get(tp_ded, f'Tipo {tp_ded}'),
                vlr_ded_susp=Decimal(vlr_ded.text) if vlr_ded is not None else Decimal('0.00'),
                cnpj_entid_pc=cnpj.text if cnpj is not None else None,
                vlr_patroc_funp=Decimal(vlr_patroc.text) if vlr_patroc is not None else None,
                benef_pen=beneficiarios
            )
        except Exception as e:
            logger.warning(f"Erro ao parse dedução suspensa: {e}")
            return None
    
    def _parse_info_valores(self, info_val_elem) -> Optional[InfoValores]:
        """Parse de valores de processo"""
        try:
            ind_apur = info_val_elem.find('esocial:indApuracao', self.NS)
            vlr_nao_ret = info_val_elem.find('esocial:vlrNRetido', self.NS)
            vlr_dep = info_val_elem.find('esocial:vlrDepJud', self.NS)
            vlr_comp_ano = info_val_elem.find('esocial:vlrCmpAnoCal', self.NS)
            vlr_comp_ant = info_val_elem.find('esocial:vlrCmpAnoAnt', self.NS)
            vlr_rend_susp = info_val_elem.find('esocial:vlrRendSusp', self.NS)
            
            # Parse deduções suspensas
            ded_susp_list = []
            for ded in info_val_elem.findall('esocial:dedSusp', self.NS):
                d = self._parse_ded_susp(ded)
                if d:
                    ded_susp_list.append(d)
            
            return InfoValores(
                ind_apuracao=ind_apur.text if ind_apur is not None else "",
                vlr_nao_retido=Decimal(vlr_nao_ret.text) if vlr_nao_ret is not None else Decimal('0.00'),
                vlr_dep_judicial=Decimal(vlr_dep.text) if vlr_dep is not None else Decimal('0.00'),
                vlr_comp_ano=Decimal(vlr_comp_ano.text) if vlr_comp_ano is not None else Decimal('0.00'),
                vlr_comp_anos_ant=Decimal(vlr_comp_ant.text) if vlr_comp_ant is not None else Decimal('0.00'),
                vlr_rend_susp=Decimal(vlr_rend_susp.text) if vlr_rend_susp is not None else Decimal('0.00'),
                ded_susp=ded_susp_list
            )
        except Exception as e:
            logger.warning(f"Erro ao parse info valores: {e}")
            return None
    
    def _parse_ded_depen(self, ded_elem) -> Optional[DedDepen]:
        """Parse de dedução por dependente"""
        try:
            tp_rend = ded_elem.find('esocial:tpRend', self.NS)
            cpf_dep = ded_elem.find('esocial:cpfDep', self.NS)
            vlr_ded = ded_elem.find('esocial:vlrDedDep', self.NS)
            
            return DedDepen(
                tp_rend=tp_rend.text if tp_rend is not None else "",
                cpf_dep=cpf_dep.text if cpf_dep is not None else "",
                vlr_ded_dep=Decimal(vlr_ded.text) if vlr_ded is not None else Decimal('0.00')
            )
        except Exception as e:
            logger.warning(f"Erro ao parse dedução dependente: {e}")
            return None
    
    def _parse_info_ir_cr(self, info_cr_elem) -> Optional[InfoIRCR]:
        """Parse de informações por código de receita"""
        try:
            tp_cr = info_cr_elem.find('esocial:tpCR', self.NS)
            
            # Tentar tag oficial primeiro, depois fallback para alias
            vr_cr = info_cr_elem.find('esocial:vlrCR', self.NS)
            if vr_cr is None:
                vr_cr = info_cr_elem.find('esocial:vrCR', self.NS)  # Fallback
                if vr_cr is not None:
                    logger.warning("Tag 'vrCR' é um alias. Use 'vlrCR' (oficial)")
            
            # Parse deduções por dependente
            ded_depen_list = []
            for ded in info_cr_elem.findall('esocial:dedDepen', self.NS):
                d = self._parse_ded_depen(ded)
                if d:
                    ded_depen_list.append(d)
            
            # Parse pensões
            pensoes = []
            for pen in info_cr_elem.findall('esocial:penAlim', self.NS):
                p = self._parse_pensao(pen)
                if p:
                    pensoes.append(p)
            
            # Parse previdência
            previdencias = []
            for prev in info_cr_elem.findall('esocial:previdCompl', self.NS):
                p = self._parse_previdencia(prev)
                if p:
                    previdencias.append(p)
            
            # Parse processos
            processos = []
            for proc in info_cr_elem.findall('esocial:infoProcRet', self.NS):
                # Parse completo com info_valores
                tp_proc = proc.find('esocial:tpProcRet', self.NS)
                nr_proc = proc.find('esocial:nrProcRet', self.NS)
                cod_susp = proc.find('esocial:codSusp', self.NS)
                
                info_valores_list = []
                for info_val in proc.findall('esocial:infoValores', self.NS):
                    iv = self._parse_info_valores(info_val)
                    if iv:
                        info_valores_list.append(iv)
                
                processos.append(ProcessoJudicial(
                    tp_proc_ret=tp_proc.text if tp_proc is not None else "",
                    nr_proc_ret=nr_proc.text if nr_proc is not None else "",
                    cod_susp=cod_susp.text if cod_susp is not None else "",
                    info_valores=info_valores_list
                ))
            
            return InfoIRCR(
                tp_cr=tp_cr.text if tp_cr is not None else "",
                vr_cr=Decimal(vr_cr.text) if vr_cr is not None else Decimal('0.00'),
                ded_depen=ded_depen_list,
                pen_alim=pensoes,
                previd_compl=previdencias,
                info_proc_ret=processos
            )
        except Exception as e:
            logger.warning(f"Erro ao parse info IR CR: {e}")
            return None
    
    def _parse_info_proc_jud_rub(self, proc_elem) -> Optional[InfoProcJudRub]:
        """Parse de processo judicial por rubrica"""
        try:
            nr_proc = proc_elem.find('esocial:nrProc', self.NS)
            uf_vara = proc_elem.find('esocial:ufVara', self.NS)
            cod_munic = proc_elem.find('esocial:codMunic', self.NS)
            id_vara = proc_elem.find('esocial:idVara', self.NS)
            
            return InfoProcJudRub(
                nr_proc=nr_proc.text if nr_proc is not None else "",
                uf_vara=uf_vara.text if uf_vara is not None else "",
                cod_munic=cod_munic.text if cod_munic is not None else "",
                id_vara=id_vara.text if id_vara is not None else ""
            )
        except Exception as e:
            logger.warning(f"Erro ao parse processo judicial rubrica: {e}")
            return None
    
    def _parse_tot_apur_dia(self, tot_elem) -> Optional[TotApurDia]:
        """Parse de totalizador diário"""
        try:
            per_apur = tot_elem.find('esocial:perApurDia', self.NS)
            cr_dia = tot_elem.find('esocial:CRDia', self.NS)
            frm_trib = tot_elem.find('esocial:frmTribut', self.NS)
            pais = tot_elem.find('esocial:paisResidExt', self.NS)
            vlr_rend = tot_elem.find('esocial:vlrRendTrib', self.NS)
            
            # Tentar tag oficial primeiro, depois fallback para alias
            vlr_irrf = tot_elem.find('esocial:vlrCRDia', self.NS)
            if vlr_irrf is None:
                vlr_irrf = tot_elem.find('esocial:vlrIRRF', self.NS)  # Fallback
                if vlr_irrf is not None:
                    logger.warning("Tag 'vlrIRRF' é um alias. Use 'vlrCRDia' (oficial)")
            
            return TotApurDia(
                per_apur_dia=per_apur.text if per_apur is not None else "",
                cr_dia=cr_dia.text if cr_dia is not None else "",
                frm_tribut=frm_trib.text if frm_trib is not None else "",
                pais_resid_ext=pais.text if pais is not None else None,
                vlr_rend_trib=Decimal(vlr_rend.text) if vlr_rend is not None else Decimal('0.00'),
                vlr_irrf=Decimal(vlr_irrf.text) if vlr_irrf is not None else Decimal('0.00')
            )
        except Exception as e:
            logger.warning(f"Erro ao parse totalizador diário: {e}")
            return None
    
    def _parse_consolid_apur_men(self, cons_elem) -> Optional[ConsolidApurMen]:
        """Parse de consolidação mensal"""
        try:
            cr_men = cons_elem.find('esocial:CRMen', self.NS)
            vlr_rend = cons_elem.find('esocial:vlrRendTrib', self.NS)
            vlr_rend13 = cons_elem.find('esocial:vlrRendTrib13', self.NS)
            
            # Tentar tags oficiais primeiro, depois fallback para aliases
            vlr_irrf = cons_elem.find('esocial:vlrCRMen', self.NS)
            if vlr_irrf is None:
                vlr_irrf = cons_elem.find('esocial:vlrIRRF', self.NS)  # Fallback
                if vlr_irrf is not None:
                    logger.warning("Tag 'vlrIRRF' é um alias. Use 'vlrCRMen' (oficial)")
            
            vlr_irrf13 = cons_elem.find('esocial:vlrCRMen13', self.NS)
            if vlr_irrf13 is None:
                vlr_irrf13 = cons_elem.find('esocial:vlrIRRF13', self.NS)  # Fallback
                if vlr_irrf13 is not None:
                    logger.warning("Tag 'vlrIRRF13' é um alias. Use 'vlrCRMen13' (oficial)")
            
            return ConsolidApurMen(
                cr_men=cr_men.text if cr_men is not None else "",
                vlr_rend_trib=Decimal(vlr_rend.text) if vlr_rend is not None else Decimal('0.00'),
                vlr_rend_trib13=Decimal(vlr_rend13.text) if vlr_rend13 is not None else Decimal('0.00'),
                vlr_irrf=Decimal(vlr_irrf.text) if vlr_irrf is not None else Decimal('0.00'),
                vlr_irrf13=Decimal(vlr_irrf13.text) if vlr_irrf13 is not None else Decimal('0.00')
            )
        except Exception as e:
            logger.warning(f"Erro ao parse consolidação mensal: {e}")
            return None
    
    def _parse_tot_info_dm_dev(self, tot_elem) -> Optional[TotInfoDmDev]:
        """Parse de totalização dos demonstrativos - NOVO V5.2.0"""
        try:
            return TotInfoDmDev(
                vlr_tot_rend_trib=self._parse_decimal(tot_elem, 'vlrTotRendTrib'),
                vlr_tot_rend_trib_13=self._parse_decimal(tot_elem, 'vlrTotRendTrib13'),
                vlr_tot_rend_mole_grave=self._parse_decimal(tot_elem, 'vlrTotRendMoleGrave'),
                vlr_tot_rend_mole_grave_13=self._parse_decimal(tot_elem, 'vlrTotRendMoleGrave13'),
                vlr_tot_rend_isen_65=self._parse_decimal(tot_elem, 'vlrTotRendIsen65'),
                vlr_tot_rend_isen_65_13=self._parse_decimal(tot_elem, 'vlrTotRendIsen65_13'),
                vlr_tot_rend_trib_ant=self._parse_decimal(tot_elem, 'vlrTotRendTribAnt'),
                vlr_tot_rend_trib_ant_13=self._parse_decimal(tot_elem, 'vlrTotRendTribAnt13'),
                vlr_tot_rend_trib_susp=self._parse_decimal(tot_elem, 'vlrTotRendTribSusp'),
                vlr_tot_rend_trib_susp_13=self._parse_decimal(tot_elem, 'vlrTotRendTribSusp13')
            )
        except Exception as e:
            logger.warning(f"Erro ao parse totalização dos demonstrativos: {e}")
            return None
    
    def _parse_decimal(self, elem, tag_name: str) -> Decimal:
        """Helper para parse de valores decimais"""
        tag = elem.find(f'esocial:{tag_name}', self.NS)
        return Decimal(tag.text) if tag is not None and tag.text else Decimal('0.00')


class PDFGenerator:
    """Gerador de PDF do comprovante de rendimentos"""
    
    def __init__(self):
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.margin_left = 20*mm
        self.margin_right = 20*mm
        self.margin_top = 20*mm
        self.margin_bottom = 20*mm
        self.content_width = self.page_width - self.margin_left - self.margin_right
        
    def gerar_pdf(self, comprovante: ComprovanteRendimentos, output_path: str):
        """Gera o PDF do comprovante"""
        try:
            # Primeira passagem: gerar PDF e contar páginas reais
            temp_path = output_path + ".temp"
            c = canvas.Canvas(temp_path, pagesize=A4)
            total_pages_real = self._gerar_conteudo(c, comprovante, 999)  # Número alto temporário
            c.save()
            
            # Segunda passagem: gerar PDF final com paginação correta
            c = canvas.Canvas(output_path, pagesize=A4)
            self._gerar_conteudo(c, comprovante, total_pages_real)
            c.save()
            
            # Remover arquivo temporário
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.debug(f"PDF gerado com sucesso: {output_path} ({total_pages_real} páginas)")
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF {output_path}: {e}")
            raise
    
    def _calcular_total_paginas(self, c: canvas.Canvas, comprovante: ComprovanteRendimentos) -> int:
        """Calcula o número total de páginas necessárias"""
        y = self.page_height - self.margin_top
        paginas = 1
        
        # Simular desenho para calcular páginas
        y = self._simular_cabecalho(y)
        y -= 6*mm
        y = self._simular_fonte_pagadora(y)
        y -= 6*mm
        y = self._simular_beneficiario(y)
        y -= 6*mm
        y = self._simular_rendimentos_tributaveis(y)
        y -= 6*mm
        y = self._simular_rendimentos_isentos(y)
        y -= 6*mm
        y = self._simular_rendimentos_exclusivos(y)
        y -= 6*mm
        
        # Informações complementares
        if (comprovante.dependentes or comprovante.pensoes_alimenticias or 
            comprovante.previdencias_complementares or comprovante.planos_saude or
            comprovante.reembolsos_medicos):
            y, paginas_adicionais = self._simular_info_complementares(y, comprovante, paginas)
            paginas += paginas_adicionais
        
        return paginas
    
    def _simular_cabecalho(self, y: float) -> float:
        """Simula desenho do cabeçalho"""
        return y - 40*mm
    
    def _simular_fonte_pagadora(self, y: float) -> float:
        """Simula desenho da fonte pagadora"""
        return y - 20*mm
    
    def _simular_beneficiario(self, y: float) -> float:
        """Simula desenho do beneficiário"""
        return y - 20*mm
    
    def _simular_rendimentos_tributaveis(self, y: float) -> float:
        """Simula desenho dos rendimentos tributáveis"""
        return y - 35*mm
    
    def _simular_rendimentos_isentos(self, y: float) -> float:
        """Simula desenho dos rendimentos isentos"""
        return y - 40*mm
    
    def _simular_rendimentos_exclusivos(self, y: float) -> float:
        """Simula desenho dos rendimentos exclusivos"""
        return y - 20*mm
    
    def _simular_info_complementares(self, y: float, comprovante: ComprovanteRendimentos, 
                                     pagina_atual: int) -> Tuple[float, int]:
        """Simula desenho das informações complementares e retorna páginas adicionais"""
        paginas_adicionais = 0
        y_inicial = y
        
        # Título da seção
        y -= 15*mm
        
        # Dependentes
        if comprovante.dependentes:
            y -= 10*mm
            y -= len(comprovante.dependentes) * 6.5*mm
        
        # Pensões
        if comprovante.pensoes_alimenticias:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.pensoes_alimenticias) * 6.5*mm
        
        # Previdências
        if comprovante.previdencias_complementares:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.previdencias_complementares) * 6.5*mm
        
        # Planos de saúde
        if comprovante.planos_saude:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            for plano in comprovante.planos_saude:
                y -= 10*mm + len(plano.dependentes) * 5*mm
                if y < 40*mm:
                    paginas_adicionais += 1
                    y = self.page_height - self.margin_top - 10*mm
        
        # Reembolsos
        if comprovante.reembolsos_medicos:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.reembolsos_medicos) * 6.5*mm
        
        # INFO RRA
        if comprovante.info_rra:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 15*mm  # Título + conteúdo
            if comprovante.info_rra.advogados:
                y -= len(comprovante.info_rra.advogados) * 6*mm
        
        # PAGAMENTO NO EXTERIOR
        if comprovante.pagamento_exterior:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 20*mm
        
        # PROCESSOS JUDICIAIS
        if comprovante.processos_judiciais:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.processos_judiciais) * 15*mm
        
        # INFO IR CR
        if comprovante.info_ir_cr:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            for info_cr in comprovante.info_ir_cr:
                y -= 8*mm
                if info_cr.ded_depen:
                    y -= len(info_cr.ded_depen) * 6*mm
        
        # INFO PROC JUD RUB
        if comprovante.info_proc_jud_rub:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.info_proc_jud_rub) * 12*mm
        
        # TOT APUR DIA
        if comprovante.tot_apur_dia:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.tot_apur_dia) * 12*mm
        
        # TOT INFO DM DEV
        if comprovante.tot_info_dm_dev:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 20*mm
        
        # CONSOLID APUR MEN
        if comprovante.consolid_apur_men:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
            y -= len(comprovante.consolid_apur_men) * 15*mm
        
        # PER ANT
        if comprovante.per_ant:
            if y < 40*mm:
                paginas_adicionais += 1
                y = self.page_height - self.margin_top - 10*mm
            y -= 10*mm
        
        return y, paginas_adicionais
    
    def _gerar_conteudo(self, c: canvas.Canvas, comprovante: ComprovanteRendimentos, total_pages: int) -> int:
        """Gera o conteúdo completo do PDF e retorna o número real de páginas"""
        pagina_atual = 1
        y = self.page_height - self.margin_top
        
        # Cabeçalho
        y = self._desenhar_cabecalho(c, comprovante.ano, y)
        y -= 6*mm
        
        # Quadro 1: Fonte Pagadora
        y = self._desenhar_fonte_pagadora(c, comprovante.fonte_pagadora, y)
        y -= 6*mm
        
        # Quadro 2: Beneficiário
        y = self._desenhar_beneficiario(c, comprovante.beneficiario, y)
        y -= 6*mm
        
        # Quadro 3: Rendimentos Tributáveis
        y = self._desenhar_rendimentos_tributaveis(c, comprovante.rendimento_tributavel, y)
        y -= 6*mm
        
        # Quadro 4: Rendimentos Isentos
        y = self._desenhar_rendimentos_isentos(c, comprovante.rendimento_isento, y)
        y -= 6*mm
        
        # Quadro 5: Rendimentos Exclusivos
        y = self._desenhar_rendimentos_exclusivos(c, comprovante.rendimento_exclusivo, y)
        y -= 6*mm
        
        # Quadro 6: Informações Complementares
        if (comprovante.dependentes or comprovante.pensoes_alimenticias or 
            comprovante.previdencias_complementares or comprovante.planos_saude or
            comprovante.reembolsos_medicos):
            y, pagina_atual = self._desenhar_info_complementares(c, comprovante, y, pagina_atual, total_pages)
        
        # Rodapé da última página
        self._desenhar_rodape(c, y, pagina_atual, total_pages)
        
        # Retornar número real de páginas
        return pagina_atual
    
    def _desenhar_cabecalho(self, c: canvas.Canvas, ano: str, y: float) -> float:
        """Desenha o cabeçalho do comprovante"""
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.page_width / 2, y, "MINISTÉRIO DA FAZENDA")
        y -= 5*mm
        c.drawCentredString(self.page_width / 2, y, "SECRETARIA DA RECEITA FEDERAL")
        y -= 8*mm
        
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(self.page_width / 2, y, "COMPROVANTE DE RENDIMENTOS PAGOS")
        y -= 5*mm
        c.drawCentredString(self.page_width / 2, y, "E DE RETENÇÃO DE IMPOSTO DE RENDA NA FONTE")
        y -= 6*mm
        
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.page_width / 2, y, f"Ano-calendário {ano}")
        y -= 8*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_fonte_pagadora(self, c: canvas.Canvas, fonte: FontePagadora, y: float) -> float:
        """Desenha os dados da fonte pagadora"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "1. FONTE PAGADORA (PESSOA JURÍDICA OU PESSOA FÍSICA)")
        y -= 6*mm
        
        c.setFont("Helvetica", 12)
        nome_lines = simpleSplit(fonte.nome, "Helvetica", 12, self.content_width - 10*mm)
        for line in nome_lines:
            c.drawString(self.margin_left, y, f"NOME EMPRESARIAL/NOME: {line}")
            y -= 4.5*mm
        
        c.drawString(self.margin_left, y, f"CNPJ: {self._formatar_cnpj(fonte.cnpj)}")
        y -= 6*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_beneficiario(self, c: canvas.Canvas, beneficiario: Beneficiario, y: float) -> float:
        """Desenha os dados do beneficiário"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "2. PESSOA FÍSICA BENEFICIÁRIA DOS RENDIMENTOS")
        y -= 6*mm
        
        c.setFont("Helvetica", 12)
        c.drawString(self.margin_left, y, f"CPF: {self._formatar_cpf(beneficiario.cpf)}")
        y -= 4.5*mm
        
        nome_lines = simpleSplit(beneficiario.nome, "Helvetica", 12, self.content_width - 10*mm)
        for line in nome_lines:
            c.drawString(self.margin_left, y, f"NOME COMPLETO: {line}")
            y -= 4.5*mm
        
        y -= 1.5*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_rendimentos_tributaveis(self, c: canvas.Canvas, rend: RendimentoTributavel, y: float) -> float:
        """Desenha os rendimentos tributáveis"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "3. RENDIMENTOS TRIBUTÁVEIS, DEDUÇÕES E IMPOSTO RETIDO NA FONTE")
        y -= 6*mm
        
        c.setFont("Helvetica", 12)
        dados = [
            ("01. Total de Rendimentos (inclusive férias)", rend.total_rendimentos),
            ("02. Contribuição Previdenciária Oficial", rend.contrib_previdenciaria),
            ("03. Contribuição à Previdência Privada e FAPI", rend.contrib_prev_privada),
            ("04. Pensão Alimentícia", rend.pensao_alimenticia),
            ("05. Imposto de Renda Retido", rend.imposto_retido),
        ]
        
        for descricao, valor in dados:
            c.drawString(self.margin_left, y, descricao)
            c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(valor))
            y -= 4.5*mm
        
        y -= 1.5*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_rendimentos_isentos(self, c: canvas.Canvas, rend: RendimentoIsento, y: float) -> float:
        """Desenha os rendimentos isentos"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "4. RENDIMENTOS ISENTOS E NÃO TRIBUTÁVEIS")
        y -= 6*mm
        
        c.setFont("Helvetica", 12)
        dados = [
            ("01. Parcela Isenta dos Proventos de Aposentadoria (65 anos ou mais)", rend.parcela_isenta_65),
            ("02. Diárias e Ajudas de Custo", rend.diarias + rend.ajuda_custo),
            ("03. Indenizações por Rescisão de Contrato", rend.indenizacoes),
            ("04. Abono Pecuniário", rend.abono_pecuniario),
            ("05. Outros", rend.molestia_grave + rend.outros),
        ]
        
        for descricao, valor in dados:
            c.drawString(self.margin_left, y, descricao)
            c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(valor))
            y -= 4.5*mm
        
        y -= 1.5*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_rendimentos_exclusivos(self, c: canvas.Canvas, rend: RendimentoExclusivo, y: float) -> float:
        """Desenha os rendimentos com tributação exclusiva"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "5. RENDIMENTOS SUJEITOS À TRIBUTAÇÃO EXCLUSIVA (RENDIMENTO LÍQUIDO)")
        y -= 6*mm
        
        c.setFont("Helvetica", 12)
        dados = [
            ("01. Décimo Terceiro Salário", rend.decimo_terceiro),
            ("02. Outros", rend.plr + rend.rra + rend.outros),
        ]
        
        for descricao, valor in dados:
            c.drawString(self.margin_left, y, descricao)
            c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(valor))
            y -= 4.5*mm
        
        y -= 1.5*mm
        
        # Linha separadora
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 6*mm
        
        return y
    
    def _desenhar_info_complementares(self, c: canvas.Canvas, comprovante: ComprovanteRendimentos, 
                                     y: float, pagina_atual: int, total_pages: int) -> Tuple[float, int]:
        """Desenha as informações complementares no padrão dos outros quadros"""
        
        # Título do quadro
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin_left, y, "6. INFORMAÇÕES COMPLEMENTARES")
        y -= 6*mm
        
        contador = 1
        c.setFont("Helvetica", 12)
        
        # DEPENDENTES
        if comprovante.dependentes:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Dependentes")
            y -= 4.5*mm
            contador += 1
            
            # Listar dependentes
            for i, dep in enumerate(comprovante.dependentes, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                # Nome do dependente
                nome_lines = simpleSplit(dep.nome, "Helvetica", 12, self.content_width - 15*mm)
                c.drawString(self.margin_left, y, f"    {i}. Nome: {nome_lines[0]}")
                y -= 4.5*mm
                for line in nome_lines[1:]:
                    c.drawString(self.margin_left + 15*mm, y, line)
                    y -= 4.5*mm
                
                # CPF e Data de Nascimento
                c.drawString(self.margin_left, y, f"       CPF: {self._formatar_cpf(dep.cpf)}")
                c.drawRightString(self.page_width - self.margin_right, y, f"Data Nascimento: {self._formatar_data(dep.dt_nascto)}")
                y -= 4.5*mm
            
            y -= 2*mm
        
        # PENSÕES ALIMENTÍCIAS
        if comprovante.pensoes_alimenticias:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Pensões Alimentícias")
            y -= 4.5*mm
            contador += 1
            
            # Listar pensões
            for i, pensao in enumerate(comprovante.pensoes_alimenticias, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                total_pensao = pensao.valor_mensal + pensao.valor_13 + pensao.valor_plr
                c.drawString(self.margin_left, y, f"    {i}. CPF Beneficiário: {self._formatar_cpf(pensao.cpf_beneficiario)}")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(total_pensao))
                y -= 4.5*mm
            
            y -= 2*mm
        
        # PREVIDÊNCIA COMPLEMENTAR
        if comprovante.previdencias_complementares:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Previdência Complementar")
            y -= 4.5*mm
            contador += 1
            
            # Listar previdências
            for i, prev in enumerate(comprovante.previdencias_complementares, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                tipo_prev = self._obter_tipo_previdencia(prev.tp_prev)
                c.drawString(self.margin_left, y, f"    {i}. CNPJ: {self._formatar_cnpj(prev.cnpj)}")
                c.drawRightString(self.page_width - self.margin_right, y, f"Tipo: {tipo_prev}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Valor Dedutível")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(prev.valor))
                y -= 4.5*mm
            
            y -= 2*mm
        
        # PLANOS DE SAÚDE
        if comprovante.planos_saude:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Planos de Saúde Coletivo Empresarial")
            y -= 4.5*mm
            contador += 1
            
            # Listar planos
            for i, plano in enumerate(comprovante.planos_saude, 1):
                if y < 50*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                # Nome da operadora
                nome_lines = simpleSplit(plano.nome_operadora, "Helvetica", 12, self.content_width - 15*mm)
                if nome_lines:  # Verificar se a lista não está vazia
                    c.drawString(self.margin_left, y, f"    {i}. Operadora: {nome_lines[0]}")
                    y -= 4.5*mm
                    for line in nome_lines[1:]:
                        c.drawString(self.margin_left + 22*mm, y, line)
                        y -= 4.5*mm
                else:
                    # Se não houver nome, mostrar apenas o número
                    c.drawString(self.margin_left, y, f"    {i}. Operadora: (Não informada)")
                    y -= 4.5*mm
                
                # CNPJ e Registro ANS
                c.drawString(self.margin_left, y, f"       CNPJ: {self._formatar_cnpj(plano.cnpj_operadora)}")
                c.drawRightString(self.page_width - self.margin_right, y, f"Registro ANS: {plano.registro_ans}")
                y -= 4.5*mm
                
                # Valor do titular
                c.drawString(self.margin_left, y, f"       Valor Pago pelo Titular")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(plano.valor_titular))
                y -= 4.5*mm
                
                # Dependentes do plano
                if plano.dependentes:
                    for j, (cpf_dep, nome_dep, valor_dep) in enumerate(plano.dependentes, 1):
                        if y < 40*mm:
                            self._desenhar_rodape(c, y, pagina_atual, total_pages)
                            c.showPage()
                            pagina_atual += 1
                            y = self.page_height - self.margin_top
                            c.setFont("Helvetica", 12)
                        
                        # Nome do dependente
                        if nome_dep:
                            nome_dep_lines = simpleSplit(nome_dep, "Helvetica", 12, self.content_width - 25*mm)
                            if nome_dep_lines:
                                c.drawString(self.margin_left, y, f"       Dependente {j}: {nome_dep_lines[0]}")
                                y -= 4.5*mm
                                for line in nome_dep_lines[1:]:
                                    c.drawString(self.margin_left + 30*mm, y, line)
                                    y -= 4.5*mm
                        else:
                            c.drawString(self.margin_left, y, f"       Dependente {j}")
                            y -= 4.5*mm
                        
                        # CPF e valor do dependente
                        c.drawString(self.margin_left, y, f"       CPF: {self._formatar_cpf(cpf_dep)}")
                        c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(valor_dep))
                        y -= 4.5*mm
                
                y -= 2*mm
            
            y -= 2*mm
        
        # REEMBOLSOS MÉDICOS
        if comprovante.reembolsos_medicos:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Reembolsos de Despesas Médicas")
            y -= 4.5*mm
            contador += 1
            
            # Listar reembolsos
            for i, reemb in enumerate(comprovante.reembolsos_medicos, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. CNPJ Prestador: {self._formatar_cnpj(reemb.cnpj_prestador)}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Valor Reembolsado")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(reemb.valor_reembolsado))
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Valor Dedutível (Despesas Médicas)")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(reemb.valor_dedutivel))
                y -= 4.5*mm
            
            y -= 2*mm
        
        # INFO RRA
        if comprovante.info_rra:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Rendimentos Recebidos Acumuladamente (RRA)")
            y -= 4.5*mm
            contador += 1
            
            rra = comprovante.info_rra
            if rra.descricao:
                desc_lines = simpleSplit(rra.descricao, "Helvetica", 12, self.content_width - 15*mm)
                c.drawString(self.margin_left, y, f"    Descrição: {desc_lines[0]}")
                y -= 4.5*mm
                for line in desc_lines[1:]:
                    c.drawString(self.margin_left + 25*mm, y, line)
                    y -= 4.5*mm
            
            if rra.custas_judiciais > 0:
                c.drawString(self.margin_left, y, f"    Custas Judiciais")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(rra.custas_judiciais))
                y -= 4.5*mm
            
            if rra.despesas_advogados > 0:
                c.drawString(self.margin_left, y, f"    Despesas com Advogados")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(rra.despesas_advogados))
                y -= 4.5*mm
            
            if rra.advogados:
                c.drawString(self.margin_left, y, f"    Advogados:")
                y -= 4.5*mm
                for j, (cpf_cnpj, nome, valor) in enumerate(rra.advogados, 1):
                    if y < 40*mm:
                        self._desenhar_rodape(c, y, pagina_atual, total_pages)
                        c.showPage()
                        pagina_atual += 1
                        y = self.page_height - self.margin_top
                        c.setFont("Helvetica", 12)
                    
                    nome_lines = simpleSplit(nome if nome else "(sem nome)", "Helvetica", 12, self.content_width - 25*mm)
                    if nome_lines:  # Verifica se a lista não está vazia
                        c.drawString(self.margin_left, y, f"       {j}. {nome_lines[0]}")
                    else:
                        c.drawString(self.margin_left, y, f"       {j}. (sem nome)")
                    y -= 4.5*mm
                    for line in nome_lines[1:]:
                        c.drawString(self.margin_left + 20*mm, y, line)
                        y -= 4.5*mm
                    
                    c.drawString(self.margin_left, y, f"          CPF/CNPJ: {cpf_cnpj}")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(valor))
                    y -= 4.5*mm
            
            y -= 2*mm
        
        # PAGAMENTO NO EXTERIOR
        if comprovante.pagamento_exterior:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Pagamento no Exterior")
            y -= 4.5*mm
            contador += 1
            
            pgto = comprovante.pagamento_exterior
            if pgto.pais:
                c.drawString(self.margin_left, y, f"    País: {pgto.pais}")
                y -= 4.5*mm
            
            if pgto.logradouro:
                logr_lines = simpleSplit(f"{pgto.logradouro}, {pgto.numero}", "Helvetica", 12, self.content_width - 15*mm)
                c.drawString(self.margin_left, y, f"    Endereço: {logr_lines[0]}")
                y -= 4.5*mm
                for line in logr_lines[1:]:
                    c.drawString(self.margin_left + 25*mm, y, line)
                    y -= 4.5*mm
            
            if pgto.complemento:
                c.drawString(self.margin_left, y, f"    Complemento: {pgto.complemento}")
                y -= 4.5*mm
            
            if pgto.bairro:
                c.drawString(self.margin_left, y, f"    Bairro: {pgto.bairro}")
                y -= 4.5*mm
            
            if pgto.cidade:
                cidade_info = f"{pgto.cidade}"
                if pgto.cod_postal:
                    cidade_info += f" - CEP: {pgto.cod_postal}"
                c.drawString(self.margin_left, y, f"    Cidade: {cidade_info}")
                y -= 4.5*mm
            
            y -= 2*mm
        
        # PROCESSOS JUDICIAIS
        if comprovante.processos_judiciais:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            # Título da subseção
            c.drawString(self.margin_left, y, f"{contador:02d}. Processos Judiciais de Não Retenção")
            y -= 4.5*mm
            contador += 1
            
            for i, proc in enumerate(comprovante.processos_judiciais, 1):
                if y < 50*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. Processo: {proc.numero_processo}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Código Suspensão: {proc.codigo_suspensao}")
                y -= 4.5*mm
                
                if proc.valor_nao_retido > 0:
                    c.drawString(self.margin_left, y, f"       Valor Não Retido")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(proc.valor_nao_retido))
                    y -= 4.5*mm
                
                if proc.deposito_judicial > 0:
                    c.drawString(self.margin_left, y, f"       Depósito Judicial")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(proc.deposito_judicial))
                    y -= 4.5*mm
                
                if proc.compensacao_ano > 0:
                    c.drawString(self.margin_left, y, f"       Compensação Ano Calendário")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(proc.compensacao_ano))
                    y -= 4.5*mm
                
                if proc.compensacao_anos_ant > 0:
                    c.drawString(self.margin_left, y, f"       Compensação Anos Anteriores")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(proc.compensacao_anos_ant))
                    y -= 4.5*mm
                
                if proc.rendimento_suspenso > 0:
                    c.drawString(self.margin_left, y, f"       Rendimento Suspenso")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(proc.rendimento_suspenso))
                    y -= 4.5*mm
                
                y -= 2*mm
            
            y -= 2*mm
        
        # ============ NOVOS GRUPOS V5.1.0 ============
        
        # INFO IR CR
        if comprovante.info_ir_cr:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Informações por Código de Receita (DIRF)")
            y -= 4.5*mm
            contador += 1
            
            for i, info_cr in enumerate(comprovante.info_ir_cr, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. Código Receita: {info_cr.tp_cr}")
                y -= 4.5*mm
                
                if info_cr.vr_cr > 0:
                    c.drawString(self.margin_left, y, f"       Valor")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(info_cr.vr_cr)))
                    y -= 4.5*mm
                
                if info_cr.ded_depen:
                    for j, ded in enumerate(info_cr.ded_depen, 1):
                        if y < 40*mm:
                            self._desenhar_rodape(c, y, pagina_atual, total_pages)
                            c.showPage()
                            pagina_atual += 1
                            y = self.page_height - self.margin_top
                            c.setFont("Helvetica", 12)
                        
                        c.drawString(self.margin_left, y, f"       Dependente: CPF {self._formatar_cpf(ded.cpf_dep)}")
                        y -= 4.5*mm
                        c.drawString(self.margin_left, y, f"       Tipo Rendimento: {ded.tp_rend}")
                        c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(ded.vlr_ded_dep)))
                        y -= 4.5*mm
            
            y -= 2*mm
        
        # INFO PROC JUD RUB
        if comprovante.info_proc_jud_rub:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Processos Judiciais por Rubrica")
            y -= 4.5*mm
            contador += 1
            
            for i, proc_rub in enumerate(comprovante.info_proc_jud_rub, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. Processo: {proc_rub.nr_proc}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       UF/Vara: {proc_rub.uf_vara}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Município: {proc_rub.cod_munic}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       ID Vara: {proc_rub.id_vara}")
                y -= 4.5*mm
            
            y -= 2*mm
        
        # TOT APUR DIA
        if comprovante.tot_apur_dia:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Totalizações Diárias")
            y -= 4.5*mm
            contador += 1
            
            for i, tot_dia in enumerate(comprovante.tot_apur_dia, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. Data: {tot_dia.per_apur_dia}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Código Receita: {tot_dia.cr_dia}")
                y -= 4.5*mm
                c.drawString(self.margin_left, y, f"       Forma Tributação: {tot_dia.frm_tribut}")
                y -= 4.5*mm
                
                if tot_dia.vlr_rend_trib > 0:
                    c.drawString(self.margin_left, y, f"       Rendimento Tributável")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot_dia.vlr_rend_trib)))
                    y -= 4.5*mm
                
                if tot_dia.vlr_irrf > 0:
                    c.drawString(self.margin_left, y, f"       IRRF Retido")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot_dia.vlr_irrf)))
                    y -= 4.5*mm
            
            y -= 2*mm
        
        # TOT INFO DM DEV - NOVO V5.2.0
        if comprovante.tot_info_dm_dev:
            if y < 80*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Totalização dos Demonstrativos")
            y -= 4.5*mm
            contador += 1
            
            tot = comprovante.tot_info_dm_dev
            
            if tot.vlr_tot_rend_trib > 0:
                c.drawString(self.margin_left, y, "    Rendimentos Tributáveis")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot.vlr_tot_rend_trib)))
                y -= 4.5*mm
            
            if tot.vlr_tot_rend_trib_13 > 0:
                c.drawString(self.margin_left, y, "    Rendimentos Tributáveis 13º")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot.vlr_tot_rend_trib_13)))
                y -= 4.5*mm
            
            if tot.vlr_tot_rend_mole_grave > 0:
                c.drawString(self.margin_left, y, "    Rendimentos Moléstia Grave")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot.vlr_tot_rend_mole_grave)))
                y -= 4.5*mm
            
            if tot.vlr_tot_rend_isen_65 > 0:
                c.drawString(self.margin_left, y, "    Rendimentos Isentos 65+")
                c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(tot.vlr_tot_rend_isen_65)))
                y -= 4.5*mm
            
            y -= 2*mm
        
        # CONSOLID APUR MEN
        if comprovante.consolid_apur_men:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Consolidações Mensais")
            y -= 4.5*mm
            contador += 1
            
            for i, cons in enumerate(comprovante.consolid_apur_men, 1):
                if y < 40*mm:
                    self._desenhar_rodape(c, y, pagina_atual, total_pages)
                    c.showPage()
                    pagina_atual += 1
                    y = self.page_height - self.margin_top
                    c.setFont("Helvetica", 12)
                
                c.drawString(self.margin_left, y, f"    {i}. Código Receita: {cons.cr_men}")
                y -= 4.5*mm
                
                if cons.vlr_rend_trib > 0:
                    c.drawString(self.margin_left, y, f"       Rendimento Tributável")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(cons.vlr_rend_trib)))
                    y -= 4.5*mm
                
                if cons.vlr_rend_trib13 > 0:
                    c.drawString(self.margin_left, y, f"       Rendimento Tributável 13º")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(cons.vlr_rend_trib13)))
                    y -= 4.5*mm
                
                if cons.vlr_irrf > 0:
                    c.drawString(self.margin_left, y, f"       IRRF Retido")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(cons.vlr_irrf)))
                    y -= 4.5*mm
                
                if cons.vlr_irrf13 > 0:
                    c.drawString(self.margin_left, y, f"       IRRF Retido 13º")
                    c.drawRightString(self.page_width - self.margin_right, y, self._formatar_valor(float(cons.vlr_irrf13)))
                    y -= 4.5*mm
            
            y -= 2*mm
        
        # PER ANT
        if comprovante.per_ant:
            if y < 50*mm:
                self._desenhar_rodape(c, y, pagina_atual, total_pages)
                c.showPage()
                pagina_atual += 1
                y = self.page_height - self.margin_top
                c.setFont("Helvetica", 12)
            
            c.drawString(self.margin_left, y, f"{contador:02d}. Informações de Períodos Anteriores")
            y -= 4.5*mm
            contador += 1
            
            c.drawString(self.margin_left, y, f"    Este comprovante contém informações de períodos anteriores.")
            y -= 4.5*mm
            
            y -= 2*mm
        
        # Linha separadora final
        if y > 40*mm:
            c.line(self.margin_left, y, self.page_width - self.margin_right, y)
            y -= 6*mm
        
        return y, pagina_atual
    
    def _desenhar_rodape(self, c: canvas.Canvas, y: float, pagina_atual: int, total_pages: int):
        """Desenha o rodapé com data/hora e paginação"""
        y_rodape = self.margin_bottom + 5*mm
        
        c.setFont("Helvetica", 10)
        data_hora = datetime.now().strftime('%d/%m/%Y às %H:%M')
        c.drawString(self.margin_left, y_rodape, f"Documento gerado eletronicamente em {data_hora}")
        
        # Paginação
        paginacao = f"Página {pagina_atual} de {total_pages}"
        c.drawRightString(self.page_width - self.margin_right, y_rodape, paginacao)
    
    def _formatar_cpf(self, cpf: str) -> str:
        """Formata CPF no padrão XXX.XXX.XXX-XX"""
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    def _formatar_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
        cnpj = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        elif len(cnpj) == 8:
            # CNPJ raiz
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/0001-XX"
        return cnpj
    
    def _formatar_valor(self, valor: float) -> str:
        """Formata valor monetário"""
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def _formatar_data(self, data: str) -> str:
        """Formata data no padrão DD/MM/AAAA"""
        if len(data) == 10 and '-' in data:
            partes = data.split('-')
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data
    
    def _obter_tipo_previdencia(self, tp_prev: str) -> str:
        """Retorna descrição do tipo de previdência"""
        tipos = {
            '1': 'PGBL',
            '2': 'FAPI',
            '3': 'Funpresp',
            '4': 'Outros'
        }
        return tipos.get(tp_prev, 'Não especificado')


class DadosComplementares:
    """Gerenciador de dados complementares (CSVs)"""
    
    def __init__(self, csv_path: Optional[str] = None, csv_dependentes: Optional[str] = None, 
                 csv_entidades: Optional[str] = None):
        self.funcionarios = {}
        self.dependentes = {}
        self.entidades = {}
        
        if csv_path and os.path.exists(csv_path):
            self._carregar_csv_funcionarios(csv_path)
        
        if csv_dependentes and os.path.exists(csv_dependentes):
            self._carregar_csv_dependentes(csv_dependentes)
        
        if csv_entidades and os.path.exists(csv_entidades):
            self._carregar_csv_entidades(csv_entidades)
    
    def _carregar_csv_funcionarios(self, csv_path: str):
        """Carrega dados do CSV de funcionários"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cpf = row.get('cpf', '').strip()
                    if cpf:
                        self.funcionarios[cpf] = {
                            'nome_funcionario': row.get('nome_funcionario', '').strip(),
                            'nome_empresa': row.get('nome_empresa', '').strip(),
                            'cnpj_empresa': row.get('cnpj_empresa', '').strip()
                        }
            logger.info(f"Carregados dados de {len(self.funcionarios)} funcionários do CSV")
        except Exception as e:
            logger.warning(f"Erro ao carregar CSV de funcionários {csv_path}: {e}")
    
    def _carregar_csv_dependentes(self, csv_path: str):
        """Carrega dados do CSV de dependentes"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cpf_titular = row.get('cpf_titular', '').strip()
                    cpf_dependente = row.get('cpf_dependente', '').strip()
                    
                    if cpf_titular and cpf_dependente:
                        if cpf_titular not in self.dependentes:
                            self.dependentes[cpf_titular] = {}
                        
                        self.dependentes[cpf_titular][cpf_dependente] = {
                            'nome': row.get('nome_dependente', '').strip(),
                            'data_nascimento': row.get('data_nascimento', '').strip(),
                            'tipo': row.get('tipo_dependente', '').strip()
                        }
            
            total_deps = sum(len(deps) for deps in self.dependentes.values())
            logger.info(f"Carregados dados de {total_deps} dependentes do CSV")
        except Exception as e:
            logger.warning(f"Erro ao carregar CSV de dependentes {csv_path}: {e}")
    
    def _carregar_csv_entidades(self, csv_path: str):
        """Carrega dados do CSV de entidades"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cnpj = row.get('cnpj', '').strip()
                    if cnpj:
                        self.entidades[cnpj] = {
                            'tipo': row.get('tipo', '').strip(),
                            'nome': row.get('nome', '').strip(),
                            'registro': row.get('registro', '').strip()
                        }
            logger.info(f"Carregados dados de {len(self.entidades)} entidades do CSV")
        except Exception as e:
            logger.warning(f"Erro ao carregar CSV de entidades {csv_path}: {e}")
    
    def obter_dados(self, cpf: str) -> Dict[str, str]:
        """Obtém dados complementares para um CPF (compatibilidade)"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        return self.funcionarios.get(cpf_limpo, {})
    
    def obter_nome_dependente(self, cpf_titular: str, cpf_dependente: str, nome_xml: str = '') -> str:
        """Obtém nome do dependente com fallback"""
        # 1. Tentar XML primeiro
        if nome_xml and nome_xml.strip():
            return nome_xml.strip()
        
        # 2. Tentar CSV de dependentes
        cpf_tit_limpo = ''.join(filter(str.isdigit, cpf_titular))
        cpf_dep_limpo = ''.join(filter(str.isdigit, cpf_dependente))
        
        if cpf_tit_limpo in self.dependentes:
            if cpf_dep_limpo in self.dependentes[cpf_tit_limpo]:
                return self.dependentes[cpf_tit_limpo][cpf_dep_limpo]['nome']
        
        # 3. Fallback
        return '(Nome não informado)'
    
    def obter_nome_entidade(self, cnpj: str, tipo: str, nome_xml: str = '') -> str:
        """Obtém nome da entidade com fallback"""
        # 1. Tentar XML primeiro
        if nome_xml and nome_xml.strip():
            return nome_xml.strip()
        
        # 2. Tentar CSV de entidades
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        if cnpj_limpo in self.entidades:
            entidade = self.entidades[cnpj_limpo]
            if entidade['tipo'] == tipo or not tipo:
                return entidade['nome']
        
        # 3. Fallback
        return '(Nome não informado)'


def processar_xml(args: Tuple[str, str, str, Optional[str], DadosComplementares]) -> Tuple[int, int]:
    """Processa um arquivo XML e gera os PDFs"""
    xml_path, output_dir, ano, csv_path, dados_compl = args
    
    try:
        # Parse do XML
        parser = S5002Parser(xml_path)
        comprovantes = parser.parse()
        
        sucesso = 0
        erros = 0
        
        # Gerar PDF para cada comprovante
        for comprovante in comprovantes:
            try:
                # Atualizar com dados complementares
                cpf = comprovante.beneficiario.cpf
                dados = dados_compl.obter_dados(cpf)
                
                # Atualizar nomes de funcionário e empresa
                if dados.get('nome_funcionario'):
                    comprovante.beneficiario.nome = dados['nome_funcionario']
                if dados.get('nome_empresa'):
                    comprovante.fonte_pagadora.nome = dados['nome_empresa']
                if dados.get('cnpj_empresa'):
                    comprovante.fonte_pagadora.cnpj = dados['cnpj_empresa']
                
                # Atualizar nomes de dependentes
                for dep in comprovante.dependentes:
                    dep.nome = dados_compl.obter_nome_dependente(cpf, dep.cpf, dep.nome)
                
                # Atualizar nomes de pensões alimentícias (dependentes)
                for pensao in comprovante.pensoes_alimenticias:
                    if hasattr(pensao, 'cpf_dep'):
                        # Tentar obter nome do dependente
                        nome_dep = dados_compl.obter_nome_dependente(cpf, pensao.cpf_dep, '')
                        if nome_dep != '(Nome não informado)':
                            pensao.nome_dep = nome_dep
                
                # Atualizar nomes de operadoras de saúde
                for plano in comprovante.planos_saude:
                    plano.nome_operadora = dados_compl.obter_nome_entidade(
                        plano.cnpj_operadora, 'plano_saude', plano.nome_operadora
                    )
                    # Atualizar nomes de dependentes no plano (usar info_dep_sau, não dependentes)
                    for dep_plano in plano.info_dep_sau:
                        dep_plano.nm_dep = dados_compl.obter_nome_dependente(
                            cpf, dep_plano.cpf_dep, dep_plano.nm_dep
                        )
                
                # Atualizar nomes de entidades de previdência
                for prev in comprovante.previdencias_complementares:
                    prev.nome_entidade = dados_compl.obter_nome_entidade(
                        prev.cnpj, 'previdencia', getattr(prev, 'nome_entidade', '')
                    )
                
                # Definir ano se não estiver definido
                if not comprovante.ano or comprovante.ano == str(datetime.now().year):
                    comprovante.ano = ano
                
                # Gerar nome do arquivo
                cpf_formatado = ''.join(filter(str.isdigit, cpf))
                if len(cpf_formatado) == 11:
                    cpf_mask = f"{cpf_formatado[:3]}_{cpf_formatado[3:6]}_{cpf_formatado[6:9]}_{cpf_formatado[9:]}"
                else:
                    cpf_mask = cpf_formatado
                
                output_path = os.path.join(output_dir, f"irpf{ano}-{cpf_mask}.pdf")
                
                # Gerar PDF
                pdf_gen = PDFGenerator()
                pdf_gen.gerar_pdf(comprovante, output_path)
                
                sucesso += 1
                
            except Exception as e:
                logger.error(f"Erro ao processar comprovante para CPF {cpf}: {e}")
                erros += 1
        
        logger.info(f"Processado {os.path.basename(xml_path)}: {sucesso} sucesso, {erros} erros")
        return sucesso, erros
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {xml_path}: {e}")
        return 0, 1


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Conversor S-5002 do e-Social para PDF - Versão Completa'
    )
    parser.add_argument('input_dir', help='Diretório contendo os arquivos XML S-5002')
    parser.add_argument('output_dir', help='Diretório para salvar os PDFs gerados')
    parser.add_argument('--ano', default=str(datetime.now().year - 1), 
                       help='Ano-calendário (padrão: ano anterior)')
    parser.add_argument('--csv', help='Arquivo CSV com dados de funcionários (cpf, nome_funcionario, cnpj, nome_empresa)')
    parser.add_argument('--csv-dependentes', help='Arquivo CSV com dados de dependentes (cpf_titular, cpf_dependente, nome_dependente, data_nascimento, tipo_dependente)')
    parser.add_argument('--csv-entidades', help='Arquivo CSV com dados de entidades (cnpj, tipo, nome, registro)')
    parser.add_argument('--workers', type=int, default=4, 
                       help='Número de workers paralelos (padrão: 4)')
    
    args = parser.parse_args()
    
    # Validar diretórios
    if not os.path.isdir(args.input_dir):
        logger.error(f"Diretório de entrada não existe: {args.input_dir}")
        sys.exit(1)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Carregar dados complementares
    dados_compl = DadosComplementares(args.csv, args.csv_dependentes, args.csv_entidades)
    
    # Listar arquivos XML
    xml_files = list(Path(args.input_dir).glob('*.xml'))
    
    if not xml_files:
        logger.warning(f"Nenhum arquivo XML encontrado em {args.input_dir}")
        sys.exit(0)
    
    logger.info(f"Encontrados {len(xml_files)} arquivo(s) XML para processar")
    if args.csv:
        logger.info(f"CSV de funcionários: {args.csv}")
    if args.csv_dependentes:
        logger.info(f"CSV de dependentes: {args.csv_dependentes}")
    if args.csv_entidades:
        logger.info(f"CSV de entidades: {args.csv_entidades}")
    logger.info(f"Processando com {args.workers} workers paralelos")
    
    # Processar arquivos em paralelo
    inicio = datetime.now()
    total_sucesso = 0
    total_erros = 0
    
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for xml_file in xml_files:
            future = executor.submit(
                processar_xml,
                (str(xml_file), args.output_dir, args.ano, args.csv, dados_compl)
            )
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                sucesso, erros = future.result()
                total_sucesso += sucesso
                total_erros += erros
            except Exception as e:
                logger.error(f"Erro no processamento: {e}")
                total_erros += 1
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    # Relatório final
    logger.info("=" * 80)
    logger.info("PROCESSAMENTO CONCLUÍDO")
    logger.info(f"Total de PDFs gerados com sucesso: {total_sucesso}")
    logger.info(f"Total de erros: {total_erros}")
    logger.info(f"Tempo total: {duracao:.2f} segundos")
    if duracao > 0:
        logger.info(f"Taxa de processamento: {total_sucesso/duracao:.2f} PDFs/segundo")
    logger.info(f"Diretório de saída: {args.output_dir}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
