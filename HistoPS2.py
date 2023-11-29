import discord
from discord.ext import commands
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

my_secret = os.environ['TOKEN']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

# Diccionario para almacenar las horas de conexión de los usuarios
# {usuario_id: {'login_time': datetime, 'logout_time': datetime}}
usuarios_horas = {}


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  # Verificar si el mensaje es un log o logout de Auraxis Bot
  if 'Auraxis Bot' in message.author.name and (
      'EPLG Login' in message.content or 'EPLG Logout' in message.content):
    await registrar_actividad_desde_mensaje(message)

  await bot.process_commands(message)


async def registrar_actividad_desde_mensaje(message):
  user_name = message.content.split('\n')[-1].strip()
  user_id = hash(
      user_name
  )  # Hash simple para simular un ID único basado en el nombre (ajustar según tus necesidades)

  ahora = datetime.now()

  if 'EPLG Login' in message.content:
    usuarios_horas[user_id] = {'login_time': ahora}
  elif 'EPLG Logout' in message.content and user_id in usuarios_horas:
    usuarios_horas[user_id]['logout_time'] = ahora
    # Generar el gráfico inmediatamente después de registrar un logout
    await generar_histograma(message.channel)


async def generar_histograma(channel, user_name=None):
  horas_conexion = []

  for usuario_id, tiempos in usuarios_horas.items():
    if 'login_time' in tiempos and 'logout_time' in tiempos:
      tiempo_conexion = tiempos['logout_time'] - tiempos['login_time']
      horas_conexion.append(tiempo_conexion.seconds // 3600)

  if horas_conexion:
    # Filtrar por nombre de usuario si se proporciona
    if user_name:
      horas_conexion = [
          tiempo_conexion for usuario_id, tiempos in usuarios_horas.items()
          if user_name.lower() in str(usuario_id).lower() for tiempo_conexion
          in [tiempos['logout_time'] - tiempos['login_time']]
          if 'login_time' in tiempos and 'logout_time' in tiempos
      ]

    # Crea el histograma
    plt.hist(horas_conexion, bins=24, range=(0, 24), edgecolor='black')
    plt.title(
        f'Histograma de horas de conexión ({user_name if user_name else "todos"})'
    )
    plt.xlabel('Hora del día')
    plt.ylabel('Número de usuarios')
    plt.grid(True)

    # Guarda la imagen del histograma
    plt.savefig('histograma.png')

    # Envía la imagen al canal de Discord
    await channel.send(file=discord.File('histograma.png'))
  else:
    await channel.send('No hay suficientes datos para generar el histograma.')


@bot.command(name='hist')
async def generar_histograma_desde_comando(ctx, user_name=None):
  await generar_histograma(ctx.channel, user_name)


bot.run(my_secret)
