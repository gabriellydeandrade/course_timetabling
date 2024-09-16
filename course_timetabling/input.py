
dia_semana = [
    "SEG",
    "TER",
    "QUA",
    "QUI",
    "SEX"
]

dia_semana_composto = [
    "SEG,QUA",
    "SEG,QUA,SEX",
    "TER,QUI",
    "QUA,SEX"
]

horarios = [
    "8:00-10:00",
    "10:00-12:00",
    "13:00-15:00",
    "15:00-17:00"
]

horarios_composto = [
    "13:00-15:00,13:00-15:00,8:00-10:00" # ALA
]


disciplinas = {
    # "ICP131_A": ["ICP131", [('SEG', '8:00-10:00'), ('QUA', '8:00-10:00')], 4],
    "ICP370": ["ICP370", [('TER', '8:00-10:00'), ('QUI', '8:00-10:00')], 4],
    "ICP489": ["ICP489", [('SEG', '8:00-10:00'), ('QUA', '8:00-10:00')], 4],
    "ICP102": ["ICP102", [('QUA', '8:00-10:00'), ('SEX', '8:00-10:00')], 4],
    "ICP142": ["ICP142", [('TER', '8:00-10:00'), ('QUI', '8:00-10:00')], 4],
    "ICP133": ["ICP133", [('TER', '13:00-15:00'), ('QUI', '13:00-15:00')], 4]
}

areas_conhecimento = {
    'HUMANAS': [
        "ICP135",
        "ICP145",
        "ICP249",
        "ICP472"
    ],
    'COMPUTACAO_CIENTIFICA': [
        "ICP115",  # Álgebra Linear Algorítmica
        "ICP238",  # Introd à Computação Numérica
        "ICP248",  # Comput Científ e Análise Dados
        "ICP351",  # Model Matemát e Computacional
        "ICP365"   # Otimização
    ],
    'CIENCIA_DE_DADOS': [
        "ICP363",  # Introd Aprendizado de Máquina (terças e quintas 13h-15h)
        "ICP532",  # Mineração de Dados (obrigatória BCMT e eletiva BCC)
        "ICP539", # Introdução ao Suporte à Decisão (obrigatória BCMT e eletiva BCC)
        "ICP103"   # Análise de Risco (obrigatória BCMT e eletiva BCC)
    ],
    'ENGENHARIA_DE_DADOS': [
        "ICP489",  # Banco de Dados I
        "ICP102", # Tecn para Grandes Vol de Dados (obrigatória BCMT e eletiva BCC)
        "ICP142"   # Organização de Dados I
    ],
    'PROGRAMACAO': [
        "ICP131",  # Programação de Computadores I
        "ICP141",  # Programação de Computadores II
        "ICP239",  # Programação Orientada a Objeto
        "ICP037"   # Oficina de Prog em C
    ],
    'ENGENHARIA_DE_SOFTWARE': [
        "ICP132",  # Processos de Software
        "ICP143",  # Projeto Prático
        "ICP237"   # Introd à Modelagem de Sistemas
    ],
    'SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO': [
        "ICP133",  # Fund de Sistemas de Computação
        "ICP246",  # Arquitet Comput e Sist Operac
        "ICP353",  # Computadores e Programação
        "ICP361",  # Programação Concorrente
        "ICP362",  # Redes de Computadores I
        "ICP473",  # Segurança da Informação
        "ICP350"   # Modelagem e Aval de Desempenho
    ],
    'TEORIA_DA_COMPUTACAO': [
        "ICP134",  # Números Inteiros Criptografia
        "ICP144",  # Matemática Discreta
        "ICP116",  # Estrutura dos Dados
        "ICP123",  # Linguagens Formais
        "ICP368",  # Algoritmos e Grafos
        "ICP370",  # Lógica e Computabilidade
        "ICP136"   # Introd Pensamento Dedutivo
    ]
}

professores = [
    "DUMMY",
    "Adriana Vivacqua",
    # "Aloisio Pina",
    # "Amaury Cruz",
    # "Anamaria Moreira",
    # "Angela Gonçalves",
    # "Carla Delgado",
    # "Carolina Marcelino",
    # "Claudson Bornstein",
    # "Daniel Bastos",
    # "Daniel Alfaro",
    "Daniel Sadoc",
    # "Eldânae Teixeira",
    # "Gabriel Pereira",
    # "Giseli Lopes",
    # "Hugo Nobrega",
    # "Hugo Musso",
    # "João Paixão",
    # "João Carlos Pereira",
    # "Jonice de Oliveira",
    # "Cabral Lima", #Josefino Cabral
    # "Juliana França",
    # "Juliana Valério",
    # "Luziane Mendonça",
    # "Marcello Goulart",
    # "Maria Helena Jardim",
    # "Maria Luiza Campos",
    # "Mauro Rincon",
    # "Mitre Dourado",
    # "Rafael Mello", # Rafael de Mello == Rafael Mello
    # "Severino Collier",
    # "Silvana Rossetto",
    # "Valéria Bastos",
    # "Vinícius Gusmão",
    # "Vivian Santos"
]

professores_area_conhecimento = {
    "DUMMY": ["*"],
    'Adriana Vivacqua': ['ENGENHARIA_DE_DADOS',
                         'ENGENHARIA_DE_SOFTWARE',
                         'HUMANAS'],
    'Ageu Pacheco': [],
    'Aloisio Pina': ['CIENCIA_DE_DADOS', 'TEORIA_DA_COMPUTACAO'],
    'Amaury Cruz': ['COMPUTACAO_CIENTIFICA'],
    'Anamaria Moreira': ['ENGENHARIA_DE_SOFTWARE', 'TEORIA_DA_COMPUTACAO'],
    'Angela Gonçalves': ['COMPUTACAO_CIENTIFICA'],
    'Cabral Lima': ['CIENCIA_DE_DADOS'],
    'Carla Delgado': ['CIENCIA_DE_DADOS', 'TEORIA_DA_COMPUTACAO', 'HUMANAS'],
    'Carolina Marcelino': ['CIENCIA_DE_DADOS'],
    'Claudson Bornstein': ['TEORIA_DA_COMPUTACAO'],
    'Daniel Alfaro': ['COMPUTACAO_CIENTIFICA'],
    'Daniel Bastos': ['TEORIA_DA_COMPUTACAO'],
    'Daniel Sadoc': ['CIENCIA_DE_DADOS',
                     'ENGENHARIA_DE_DADOS',
                     'SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO'],
    'Eldânae Teixeira': ['ENGENHARIA_DE_SOFTWARE', 'HUMANAS'],
    'Gabriel Pereira': ['SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO'],
    'Giseli Lopes': ['CIENCIA_DE_DADOS',
                     'ENGENHARIA_DE_DADOS',
                     'SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO'],
    'Hugo Musso': ['TEORIA_DA_COMPUTACAO'],
    'Hugo Nobrega': ['TEORIA_DA_COMPUTACAO'],
    'João Carlos Pereira': ['CIENCIA_DE_DADOS', 'TEORIA_DA_COMPUTACAO'],
    'João Paixão': ['COMPUTACAO_CIENTIFICA', 'TEORIA_DA_COMPUTACAO'],
    'Jonice de Oliveira': ['CIENCIA_DE_DADOS',
                           'ENGENHARIA_DE_DADOS',
                           'ENGENHARIA_DE_SOFTWARE',
                           'HUMANAS'],
    'Juliana França': ['ENGENHARIA_DE_DADOS', 'ENGENHARIA_DE_SOFTWARE'],
    'Juliana Valério': ['COMPUTACAO_CIENTIFICA'],
    'Luziane Mendonça': ['COMPUTACAO_CIENTIFICA'],
    'Marcello Goulart': ['COMPUTACAO_CIENTIFICA'],
    'Maria Helena Jardim': ['COMPUTACAO_CIENTIFICA'],
    'Maria Luiza Campos': ['ENGENHARIA_DE_DADOS',
                           'ENGENHARIA_DE_SOFTWARE',
                           'HUMANAS'],
    'Mauro Rincon': ['COMPUTACAO_CIENTIFICA'],
    'Mitre Dourado': ['TEORIA_DA_COMPUTACAO'],
    'Rafael Mello': ['ENGENHARIA_DE_SOFTWARE'],
    'Severino Collier': ['COMPUTACAO_CIENTIFICA', 'TEORIA_DA_COMPUTACAO'],
    'Silvana Rossetto': ['SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO'],
    'Valéria Bastos': ['SISTEMAS_DE_COMPUTACAO_E_COMUNICACAO'],
    'Vinícius Gusmão': ['TEORIA_DA_COMPUTACAO'],
    'Vivian Santos': ['ENGENHARIA_DE_DADOS']}
