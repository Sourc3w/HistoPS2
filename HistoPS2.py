import discord
from discord.ext import commands
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

my_secret = os.environ['TOKEN']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

# Diccionario para almacenar los datos de conexión de cada usuario
# {'usuario': {'login_time': datetime, 'logout_time': datetime}, ...}
usuarios_datos = {}


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  # Verificar si el mensaje comienza con el prefijo del bot
  if message.content.startswith(bot.command_prefix):
    await bot.process_commands(message)
  else:
    # Verificar si el mensaje contiene "EPLG Login" o "EPLG Logout"
    if 'EPLG Login' in message.content or 'EPLG Logout' in message.content:
      user_name = message.content.split('\n')[-1].strip()
      ahora = datetime.utcnow()  # Cambiado a datetime.utcnow()

      if 'EPLG Login' in message.content:
        # Agregar la hora de conexión al diccionario
        usuarios_datos[user_name] = {'login_time': ahora, 'usuario': user_name}
      elif 'EPLG Logout' in message.content:
        # Verificar si hay un login previo para este usuario
        if user_name in usuarios_datos:
          # Agregar la hora de desconexión al diccionario
          usuarios_datos[user_name]['logout_time'] = ahora


async def generar_histograma(channel, usuario=None):
  print('Generating histogram...')

  plt.clf()

  minutos = np.arange(0, 1440, 1)
  histograma = np.zeros(len(minutos))

  datos_filtrados = usuarios_datos.values() if usuario is None else [
      usuarios_datos.get(usuario, {})
  ]

  for data in datos_filtrados:
    if 'login_time' in data and 'logout_time' in data:
      inicio = data['login_time'].hour * 60 + data['login_time'].minute
      fin = data['logout_time'].hour * 60 + data['logout_time'].minute
      histograma[inicio:fin + 1] += 1

  limites = np.where(histograma > 0)[0]
  rango_inicio = max(0, min(limites) - 30)
  rango_fin = min(1440, max(limites) + 30)

  gradient_fill = histograma[rango_inicio:rango_fin] / np.max(
      histograma[rango_inicio:rango_fin])

  plt.fill_between(minutos[rango_inicio:rango_fin],
                   histograma[rango_inicio:rango_fin],
                   color=plt.cm.viridis(gradient_fill),
                   alpha=0.7)

  plt.title('Total time' if not usuario else f'Time of {usuario}')
  plt.xticks(np.arange(rango_inicio, rango_fin + 1, 60), [
      str(timedelta(minutes=m))[:-3]
      for m in range(rango_inicio, rango_fin + 1, 60)
  ],
             rotation=45,
             ha='right')
  plt.grid(True)

  # Quitar los números del eje y
  plt.yticks([])

  plt.savefig('histograma_acumulativo.png')
  await channel.send(file=discord.File('histograma_acumulativo.png'))


@bot.command(name='hist',
             help='Genera un histograma acumulativo de horas de conexión. '
             'El histograma incluye a todos los usuarios en un solo gráfico.'
             'Puedes usar $hist <usuario> para generar un histograma')
async def generar_histograma_desde_comando(ctx, usuario=None):
  await generar_histograma(ctx.channel, usuario)


bot.run(my_secret)
