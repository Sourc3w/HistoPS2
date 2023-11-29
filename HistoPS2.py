import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def registrar_actividad(member, actividad):
    ahora = datetime.now()
    hora_actual = ahora.hour

    # Añade la hora actual y el tipo de actividad al archivo de registro
    with open('registro.txt', 'a') as file:
        file.write(f'{member.name} {actividad} a las {hora_actual} horas\n')

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name}')

@bot.event
async def on_member_update(before, after):
    if before.activity != after.activity:
        actividad_anterior = before.activity.name if before.activity else "desconocida"
        actividad_actual = after.activity.name if after.activity else "desconocida"

        if actividad_anterior != actividad_actual:
            if actividad_anterior != "desconocida":
                await registrar_actividad(after, "Logout")
            if actividad_actual != "desconocida":
                await registrar_actividad(after, "Login")

@bot.command(name='histograma')
async def generar_histograma(ctx, tipo_actividad):
    horas = []

    # Lee el archivo de registro y extrae las horas según el tipo de actividad
    with open('registro.txt', 'r') as file:
        for line in file:
            if f'{tipo_actividad} a las' in line:
                hora = int(line.split()[-2])
                horas.append(hora)

    if not horas:
        await ctx.send(f'No hay registros de actividad del tipo {tipo_actividad}.')
        return

    # Crea el histograma
    plt.hist(horas, bins=24, range=(0, 24), edgecolor='black')
    plt.title(f'Histograma de horas de {tipo_actividad}')
    plt.xlabel('Hora del día')
    plt.ylabel('Número de eventos')
    plt.grid(True)

    # Guarda la imagen del histograma
    plt.savefig('histograma.png')

    # Envía la imagen al canal de Discord
    await ctx.send(file=discord.File('histograma.png'))

# Reemplaza 'TOKEN_DEL_BOT' con el token real de tu bot
bot.run('TOKEN_DEL_BOT')
