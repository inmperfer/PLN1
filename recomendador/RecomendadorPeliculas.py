

##########################################################################
#####  Sistema de recomendación de películas
#####      PLNCD
#####          Jose F Quesada
##########################################################################

##########################################################################
### Paso 1: Leer ficheros con las sinopsis de las películas
##########################################################################

###
### Utilizaremos el dataset disponible en
###
###    http://www.cs.cmu.edu/~ark/personas/
###
### En concreto el fichero
###
###    http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz
###
### que una vez descomprimido genera los siguientes ficheros
###
### character.metadata.tsv
### movie.metadata.tsv
### name.clusters.txt
### plot_summaries.txt
### README.txt
### tvtropes.clusters.txt
###
### De esta distribución utilizaremos el fichero
###
###     movie.metadata.tsv
###
### cada línea de este fichero contiene los metadatos básicos de
### una película, separados por un tabulador, como muestra el siguiente
### ejemplo:
###
### 975900	/m/03vyhn	Ghosts of Mars	2001-08-24	14010832	98.0	{"/m/02h40lc": "English
### Language"}	{"/m/09c7w0": "United States of America"}	{"/m/01jfsb": "Thriller", "/m/06n90": "S
### cience Fiction", "/m/03npn": "Horror", "/m/03k9fj": "Adventure", "/m/0fdjb": "Supernatural", "/m/02kdv5l
### ": "Action", "/m/09zvmj": "Space western"}
###
### El primer elemento indica el código de película (975900). Tras un código
### de referencia aparece el título (Ghosts of Mars) y a continuación la fecha.
###
### El segundo fichero que utilizaremos es
###
###     plot_summaries.txt
###
### que contiene la sinopsis o resumen de cada película. Cada línea comienza
### con el código de película, y a continuación el texto correspondiente.
###

import ast
import nltk
#nltk.download()


def getListOfGenres(genres_metadata):
    return list(ast.literal_eval(genres_metadata).values())

    

def leerPeliculas(maxPeliculas = 0):
    ## Creamos un diccionario inicial para contener todas
    ## las películas que vamos a leer
    ##
    ## Cada entrada de este diccionario será una película indexada
    ## en el diccionario por el código de película

    peliculas = {}

    ## Fase 1: Comenzamos leyendo los metadatos
    ficheroMetadatos = open("MovieSummaries/movie.metadata.tsv", "r", encoding="utf-8")
    contadorMetadatos = 0

    for pelicula in ficheroMetadatos:
        contadorMetadatos += 1

        metadatos = pelicula.split('\t')

        # metadatos[0] -> Código de la película
        codigoPelicula = metadatos[0]
        # metadatos[1] -> Referencia (ignorar)
        # metadatos[2] -> Título
        tituloPelicula = metadatos[2]
        # metadatos[3] -> Fecha
        fechaPelicula = metadatos[3]
 
        # metadatos[8] -> Géneros
        generosPelicula = metadatos[8]


        pelicula = {}
        pelicula['codigo'] = codigoPelicula
        pelicula['titulo'] = tituloPelicula
        pelicula['fecha'] = fechaPelicula
        pelicula['generos'] = getListOfGenres(generosPelicula)
        
        
        peliculas[codigoPelicula] = pelicula

    ## Fase 2: Leemos las sinopsis de las películas y las
    ## vinculamos a la entrada del diccionario correspondiente

    ficheroSinopsis = open("MovieSummaries/plot_summaries.txt","r", encoding="utf-8")
    contadorSinopsis = 0

    for lineaSinopsis in ficheroSinopsis:
        # print(pelicula)
        contadorSinopsis += 1

        datosSinopsis = lineaSinopsis.split('\t')
        # datosSinopsis[0] -> Código de película
        codigoPelicula = datosSinopsis[0]
        # datosSinopsis[1] -> Sinopsis de la película
        resumenPelicula = datosSinopsis[1]

        pelicula = peliculas.get(codigoPelicula, 0)

        if (pelicula != 0):
            pelicula['resumen'] = resumenPelicula
            peliculas[codigoPelicula] = pelicula

    ## Fase 3: Creamos un nuevo diccionario que solo tenga las películas
    ## para cuyos metadatos hayamos encontrado un resumen

    peliculasCompletas = {}
    contadorCompletas = 0
    for peliculaCodigo in peliculas:
        pelicula = peliculas[peliculaCodigo]

        resumen = pelicula.get('resumen',0)
        generos = pelicula.get('generos', 0)
        if ((resumen != 0)  and (generos!=0) and (len(generos)> 0)):
            contadorCompletas += 1
            peliculasCompletas[peliculaCodigo] = pelicula

            if ((maxPeliculas > 0) & (contadorCompletas >= maxPeliculas)):
                break;

    print("Total Metadatos = ", contadorMetadatos)
    print("Total Sinopsis  = ", contadorSinopsis)
    print("Total Peliculas = ", contadorCompletas)

    return peliculasCompletas



##########################################################################
### Paso 2: Preprocesado y limpieza de los resúmenes de las películas
##########################################################################


from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))

# Stemmers remove morphological affixes from words, leaving only the word stem.
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer("english")

# obtengo nombres propios para añadirlo a stop words, porque no es relevante para nuestro estudio
def obtenerNombresPropios(nombres, texto):
    # Recorremos todas las oraciones de un texto (resumen de una película)

    for frase in nltk.sent_tokenize(texto):
        #
        # nltk.word_tokenize devuelve la lista de palabras que forman
        #    la frase (tokenización)
        #
        # nltk.pos_tag devuelve el part of speech (categoría) correspondiente
        #    a la palabra introducida
        #
        # nltk.ne_chunk devuelve la etiqueta correspondiente al part of
        #    speech
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(frase))):
            try:
                if chunk.label() == 'PERSON':
                    for c in chunk.leaves():
                        if str(c[0].lower()) not in nombres:
                            nombres.append(str(c[0]).lower())
            except AttributeError:
                pass
    return nombres

# Separa las palabras del texto
# cojo la palabra la pongo en minusculas y le busco la raiz
# palabras es generico para todo el repositorio de peliculas
def preprocesarPeliculas(peliculas):
    print("Preprocesando películas")
    nombresPropios = []

    for elemento in peliculas:
        #print("Preproceso: ",elemento)

        pelicula = peliculas[elemento]

        ## Eliminación de signos de puntuación usando tokenizer
        resumen = pelicula['resumen']
        texto = ' '.join(tokenizer.tokenize(resumen))
        pelicula['texto'] = texto

        nombresPropios = obtenerNombresPropios(nombresPropios, texto)

    ignoraPalabras = stopWords
    ignoraPalabras.union(nombresPropios)

    palabras = [[]]
    for elemento in peliculas:
        pelicula = peliculas[elemento]

        texto = pelicula['texto']
        textoPreprocesado = []
        for palabra in tokenizer.tokenize(texto):  
            if (palabra.lower() not in ignoraPalabras):
                textoPreprocesado.append(stemmer.stem(palabra.lower()))
                palabras.append([(stemmer.stem(palabra.lower()))])

        pelicula['texto'] = ' '.join(textoPreprocesado)
        
    return palabras

##########################################################################
### Paso 3: Creación de la colección de textos
##########################################################################


    
def crearColeccionTextos(peliculas):
    print("Creando colección global de resúmenes")
    textos = []
    
    for elemento in peliculas:
        pelicula = peliculas[elemento]
        texto = pelicula['texto']
        lista = texto.split(' ')

        textos.append(lista)

    return textos


def crearColeccionGeneros(peliculas):
    print("Creando colección global de géneros")
    generos = []
    
    for elemento in peliculas:
        pelicula = peliculas[elemento]
        genero = pelicula['generos']
        
        generos.append(genero)

    return generos
##########################################################################
### Paso 4: Creación del diccionario de palabras
##########################################################################
###
### El diccionario está formado por la concatenación de todas las
### palabras que aparecen en alguna sinopsis (modo texto) de alguna
### de las peliculas
###
### Básicamente esta función mapea cada palabra única con su identificador
###
### Es decir, si tenemos N palabras, lo que conseguiremos al final
### es que cada película sea representada mediante un vector en un
### espacio de N dimensiones

# Mapea cada palabra con un identificador unico
def crearDiccionario(textos):
    print("Creación del diccionario global")
    return corpora.Dictionary(textos)
    

##########################################################################
### Paso 5: Creación del corpus de resúmenes preprocesados
##########################################################################
###
### Crearemos un corpus con la colección de todos los resúmenes
### previamente pre-procesados y transformados usando el diccionario
###

def crearCorpus(diccionario, coleccion):
    print("Creación del corpus global")
    return [diccionario.doc2bow(texto) for texto in coleccion]

            

### En este momento podemos revisar el contenido de la información
### obtenida.

### Consideremos por ejemplo la película "Mary Poppins" cuyo
### código en el Data Set es 77856

### >>> peliculas['77856']['titulo']
### 'Mary Poppins'
### >>> peliculas['77856']['fecha']
### '1964-08-27'
### >>> peliculas['77856']['resumen'][:200]
###'The film opens with Mary Poppins  perched in a cloud high above London in spring 1910."... It\'s grand to be an Englishman in 1910 / King Edward\'s on the throne; it\'s the age of men! ..." George Banks\''
### >>> peliculas['77856']['texto'][:200]
### 'the film open with mari poppin perch in a cloud high abov london in spring 1910 it s grand to be an englishman in 1910 king edward s on the throne it s the age of men georg bank open song the life i l'

### Esta película ocupa el índice 8 (novena película) entre las que hemos leído
###
### Esto nos indica que la entrada 8 de corpus contiene 554 tokens (palabras distintas)
###
### >>> len(corpus[8])
### 554
###
### Si observamos las primeras 20 entradas de corpus[8], podemos determinar
### que la palabra de índice 0 aparece 1 vez en el texto resumen de esta
### película, mientras que la palabra 2 aparece 117 veces
###
### >>> corpus[8][:20]
### [(0, 1), (1, 18), (2, 117), (4, 1), (5, 36), (8, 1), (11, 12), (12, 42), (14, 16), (15, 4), (21, 44), (22, 1), (23, 7), (25, 2), (31, 1), (34, 14), (35, 1), (37, 1), (39, 1), (53, 4)]
###
### Para ver la palabra exacta a la que se refiere cada índice podemos
### utilizar el diccionario
### >>> diccionario[0]
### 'set'
### >>> diccionario[2]
### 'the'
### >>> diccionario[34]
### 'with'

### La siguiente instrucción nos permite obtener la lista de tuplas
### con la palabra, su índice y el número de repeticiones asociadas
### a esta película
###
### >>> [(diccionario[n],n,m) for (n,m) in corpus[8]]
###
### >>> diccionario[1028]
### 'supercalifragilisticexpialidoci'

##########################################################################
### Paso 6: Creación del modelo tf-idf
##########################################################################

# documentos como palabras tiene el corpus
def crearTfIdf(corpus):
    print("Creación del Modelo Espacio-Vector Tf-Idf")
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    return corpus_tfidf


'''
### >>> print(corpus[8][:20])
### [(0, 1), (1, 18), (2, 117), (4, 1), (5, 36), (8, 1), (11, 12), (12, 42), (14, 16), (15, 4), (21, 44), (22, 1), (23, 7), (25, 2), (31, 1), (34, 14), (35, 1), (37, 1), (39, 1), (53, 4)]
### >>> print(sinop_tfidf[8][:20])
### [(0, 0.00762910434797757), (1, 0.025451519972774662), (4, 0.010198378012720392), (8, 0.00762910434797757), (11, 0.008011540113419483), (14, 0.01068205348455931), (15, 0.005655893327283258), (22, 0.00762910434797757), (23, 0.015820766458248765), (25, 0.020396756025440783), (31, 0.005806175672270604), (34, 0.009346796798989396), (35, 0.00762910434797757), (37, 0.00762910434797757), (39, 0.00762910434797757), (53, 0.012947608030111121), (57, 0.005806175672270604), (60, 0.03051641739191028), (61, 0.0323690200752778), (65, 0.017568809361799154)]
'''


##########################################################################
### Paso 7: Creación del modelo LSA (Latent Semantic Analysis)
##########################################################################

# la dimension en la que trabajamos es muy elevada (len(diccionario))
# vamos a usar una técnica para reducir la dimensionalidad (latent semantic analysis, LSA) Tambien LSI
# lo consigue con operaciones matriciales. Es un modelo puramente matemático
from gensim import corpora, models, similarities

def crearLSA(corpus, matrix_tfidf, diccionario, num_topics):
    print("Creación del modelo LSA (Latent Semantic Analysis)")
    print("Dimensiones = {0}".format(num_topics))
    lsi = models.LsiModel(matrix_tfidf, id2word=diccionario, num_topics=num_topics)
    indice = similarities.MatrixSimilarity(lsi[matrix_tfidf])
    return (lsi, indice)

    
    
def crearCodigosPeliculas(peliculas):
    codigosPeliculas = []
    for i, elemento in enumerate(peliculas):
        pelicula = peliculas[elemento]
        codigosPeliculas.append(pelicula['codigo'])
    return codigosPeliculas

     
def crearModeloSimilitud(peliculas,sinop_tfidf, lsi_sinop, indice_sinop, weight_sinopsis, 
                         gen_tfidf, lsi_genre, indice_genre,weight_genero, n_similares, salida=None):
    print("Creando enlaces de similitud entre películas")
    print("Peso para sinopsis = {0}".format(weight_sinopsis))
    print("Peso para género = {0}".format(weight_genero))
    print("Número de películas similares = {0}".format(n_similares))
    
    codigosPeliculas = crearCodigosPeliculas(peliculas)
    
    if (salida != None):
        print("Generando salida en fichero ", salida)
        ficheroSalida = open(salida, "w", encoding="utf-8")
        
    for i, (doc_sinop, doc_genre) in enumerate(zip(sinop_tfidf, gen_tfidf)):    
        print("============================")
        peliculaI = peliculas[codigosPeliculas[i]]
        print("[{0}] [{2}] Película I = {1}".format(i, peliculaI['titulo'], peliculaI['codigo'] ))
        
        if (salida != None):
            ficheroSalida.write("============================")
            ficheroSalida.write("\n")
            ficheroSalida.write("[{0}] [{2}] Película I = {1}".format(i, peliculaI['titulo'], peliculaI['codigo'] ))
            ficheroSalida.write("\n")
         
        vec_lsi_sinopsis = lsi_sinop[doc_sinop]
        vec_lsi_genre = lsi_genre[doc_genre]
        
        indice_similitud_sinopsis = indice_sinop[vec_lsi_sinopsis]
        indice_similitud_genre = indice_genre[vec_lsi_genre]

        similares = []
        for j, elemento in enumerate(peliculas):
            s = (weight_sinopsis * indice_similitud_sinopsis[j]) + (weight_genero * indice_similitud_genre[j])
            
            # i!j para que no me añada como pelicula similar ella misma
            if (i != j):                
                similares.append((codigosPeliculas[j], s))
                
        similares = sorted(similares, key=lambda item: -item[1])[0:n_similares]
            
        for p in similares:
            peliculaJ=peliculas[p[0]]
            print("   Similitud: {0}    ==> [{2}] Película J = {1}".format(round(p[1], 3), peliculaJ['titulo'], peliculaJ['codigo']))
            if (salida != None):
                ficheroSalida.write("   Similitud: {0}    ==> [{2}] Película J = {1}".format(round(p[1], 4), peliculaJ['titulo'], peliculaJ['codigo']))
                ficheroSalida.write("\n")
                    
        peliculaI['similares'] = similares

    if (salida != None):
        ficheroSalida.close()

#####CASO PRACTICO#####        
# LECTURA DE PELICULAS
print("=============  Lectura metadatos  ===============")
peliculas   = leerPeliculas(50)

# MATRIZ DE SIMILITUDES DEL METADATO SINOPSIS
print("=============  Matriz similitud para Sinopsis  ===============")
TOTAL_TOPICOS_LSA_SINOPSIS = 300 
palabras    = preprocesarPeliculas(peliculas)
textos      = crearColeccionTextos(peliculas)
diccionario = crearDiccionario(textos)
corpus      = crearCorpus(diccionario, textos)
sinop_tfidf   = crearTfIdf(corpus)
(lsi_sinop, indice_sinop)= crearLSA(corpus, sinop_tfidf, diccionario, TOTAL_TOPICOS_LSA_SINOPSIS)


# MATRIZ DE SIMILITUDES DEL METADATO GENERO
print("=============  Matriz similitModeloud para Género  ===============")

TOTAL_TOPICOS_LSA_GENERO = 82        


genres     = crearColeccionGeneros(peliculas)
diccionario_genre = crearDiccionario(genres)
corpus_genre = crearCorpus(diccionario_genre, genres)
gen_tfidf   = crearTfIdf(corpus_genre)
(lsi_genre, indice_genre)= crearLSA(corpus_genre, gen_tfidf, diccionario_genre, TOTAL_TOPICOS_LSA_GENERO)

# MODELO SIMILITUD SINOPSIS + GÉNERO
print("=============  Creación modelo similitud Películas ===============")
WEIGHT_SINOPSIS=0.7
WEIGHT_GENERO=0.3 
N_SIMILITUD = 4 

crearModeloSimilitud(peliculas,sinop_tfidf, lsi_sinop, indice_sinop, WEIGHT_SINOPSIS, 
                         gen_tfidf, lsi_genre, indice_genre, WEIGHT_GENERO, N_SIMILITUD, salida='similitudes.txt')
