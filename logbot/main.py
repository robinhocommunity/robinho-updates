import discord, os
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("ERRO: Variavel DISCORD_BOT_TOKEN nao definida")
    exit(1)

GUILD_ID = 1521256151285760152
LOG_ENTROU = 1521256857233264650
LOG_SAIU = 1521256858273448040
LOG_MENSAGENS = 1521257243675328712
LOG_CANAIS = 1521257275208106004
LOG_CARGOS = 1521257260918247445
LOG_MODERACAO = 1521257278697767002
LOG_SERVER = 1521257257331851534
LOG_USERS = 1521257271290626048
LOG_VENDAS = 1521256856155328592
LOG_CMD = 1521256861687480400

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.moderation = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

def embed(title, desc, color=0x5865F2, fields=None):
    e = discord.Embed(title=title, description=desc, color=color, timestamp=discord.utils.utcnow())
    if fields:
        for name, value in fields:
            e.add_field(name=name, value=value, inline=False)
    return e

async def send_log(channel_id, emb):
    ch = bot.get_channel(channel_id)
    if ch:
        await ch.send(embed=emb)

@bot.event
async def on_ready():
    print(f"Bot log ativo: {bot.user}")

@bot.event
async def on_member_join(member):
    e = embed("Membro Entrou", f"{member.mention} ({member.name})", 0x57F287,
              [("Conta criada", discord.utils.format_dt(member.created_at, "R")),
               ("ID", member.id)])
    await send_log(LOG_ENTROU, e)

@bot.event
async def on_member_remove(member):
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    e = embed("Membro Saiu", f"{member.mention} ({member.name})", 0xED4245,
              [("Cargos", " ".join(roles) if roles else "Nenhum"),
               ("ID", member.id)])
    await send_log(LOG_SAIU, e)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    e = embed("Mensagem Editada", f"**Canal:** {before.channel.mention}\n**Autor:** {before.author.mention}", 0xFEE75C,
              [("Antes", before.content or "*sem conteudo*"),
               ("Depois", after.content or "*sem conteudo*")])
    await send_log(LOG_MENSAGENS, e)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    e = embed("Mensagem Deletada", f"**Canal:** {message.channel.mention}\n**Autor:** {message.author.mention}", 0xED4245,
              [("Conteudo", message.content or "*sem conteudo*")])
    await send_log(LOG_MENSAGENS, e)

@bot.event
async def on_guild_channel_create(channel):
    e = embed("Canal Criado", f"**Nome:** {channel.name}\n**Tipo:** {channel.type}\n**Categoria:** {channel.category}", 0x57F287)
    await send_log(LOG_CANAIS, e)

@bot.event
async def on_guild_channel_delete(channel):
    e = embed("Canal Deletado", f"**Nome:** {channel.name}\n**Tipo:** {channel.type}", 0xED4245)
    await send_log(LOG_CANAIS, e)

@bot.event
async def on_guild_role_create(role):
    e = embed("Cargo Criado", f"{role.mention}", 0x57F287)
    await send_log(LOG_CARGOS, e)

@bot.event
async def on_guild_role_delete(role):
    e = embed("Cargo Deletado", f"**{role.name}**", 0xED4245)
    await send_log(LOG_CARGOS, e)

@bot.event
async def on_guild_role_update(before, after):
    if before.name != after.name:
        e = embed("Cargo Renomeado", f"{after.mention}\n**Antes:** {before.name}\n**Depois:** {after.name}", 0xFEE75C)
        await send_log(LOG_CARGOS, e)

@bot.event
async def on_member_ban(guild, user):
    e = embed("Membro Banido", f"{user.mention} ({user.name})", 0xED4245,
              [("ID", user.id)])
    await send_log(LOG_MODERACAO, e)

@bot.event
async def on_member_unban(guild, user):
    e = embed("Membro Desbanido", f"{user.mention} ({user.name})", 0x57F287,
              [("ID", user.id)])
    await send_log(LOG_MODERACAO, e)

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        e = embed("Nickname Alterado", f"{after.mention}", 0xFEE75C,
                  [("Antes", before.nick or "*nenhum*"),
                   ("Depois", after.nick or "*nenhum*")])
        await send_log(LOG_USERS, e)
    elif before.roles != after.roles:
        added = [r.mention for r in after.roles if r not in before.roles and r.name != "@everyone"]
        removed = [r.mention for r in before.roles if r not in after.roles and r.name != "@everyone"]
        if added:
            e = embed("Cargo Adicionado", f"{after.mention}\n{' '.join(added)}", 0x57F287)
            await send_log(LOG_USERS, e)
        if removed:
            e = embed("Cargo Removido", f"{after.mention}\n{' '.join(removed)}", 0xED4245)
            await send_log(LOG_USERS, e)

@bot.event
async def on_guild_update(before, after):
    if before.name != after.name:
        e = embed("Servidor Renomeado", f"**Antes:** {before.name}\n**Depois:** {after.name}", 0xFEE75C)
        await send_log(LOG_SERVER, e)
    if before.icon != after.icon:
        e = embed("Icone Alterado", "", 0xFEE75C)
        await send_log(LOG_SERVER, e)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if after.channel and not before.channel:
            e = embed("Entrou no Voz", f"{member.mention} -> {after.channel.name}", 0x57F287)
            await send_log(LOG_MENSAGENS, e)
        elif before.channel and not after.channel:
            e = embed("Saiu do Voz", f"{member.mention} <- {before.channel.name}", 0xED4245)
            await send_log(LOG_MENSAGENS, e)
        else:
            e = embed("Mudou de Voz", f"{member.mention}: {before.channel.name} -> {after.channel.name}", 0xFEE75C)
            await send_log(LOG_MENSAGENS, e)

bot.run(TOKEN)
