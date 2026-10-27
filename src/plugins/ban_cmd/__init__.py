import asyncio
from nonebot import on_notice, logger
from nonebot.adapters.onebot.v11 import Bot, GroupBanNoticeEvent, MessageSegment

# 监听群禁言通知事件
ban_cmd_matcher = on_notice(priority=1, block=True)

# 禁言秒数 -> 对应指令响应
COMMAND_MAP = {
    26: (
        "【帮助菜单】\n"
        "- 禁言 26 秒: 查看本帮助（需等待 27 秒）\n"
        "- 禁言 60 秒: 触发摸鱼问候\n"
        "- 禁言 120 秒: 查看系统健康与延时状态\n"
        "提示: 必须管理员给 Bot 禁言指定时长，解禁后自动响应。"
    ),
    60: "你禁言了我 60 秒，我已经摸完一整条鱼回来了。",
    120: "【系统状态】\n- 运行状态: 良好\n- 指令延时: 极高（物理禁言前摇）\n- 用户体验: 已成功践踏至地心",
}

@ban_cmd_matcher.handle()
async def handle_ban_command(bot: Bot, event: GroupBanNoticeEvent):
    # 仅响应针对 Bot 自身的群禁言事件
    if event.sub_type != "ban":
        return
    if event.user_id != int(bot.self_id):
        return

    duration = event.duration
    logger.info(f"Bot 收到来自管理员 {event.operator_id} 的禁言事件，时长: {duration}s")

    if duration not in COMMAND_MAP:
        logger.debug(f"未匹配到禁言时长 {duration}s 对应的指令，忽略")
        return

    # 因为被禁言期间在群内发言会被协议层拒绝，必须强行睡眠等待禁言结束 (+1s 缓冲)
    wait_time = duration + 1
    logger.info(f"指令匹配成功！进入前摇等待: 等待 {wait_time} 秒后输出指令结果...")
    await asyncio.sleep(wait_time)

    # 禁言解除后在群内发送执行结果
    reply_msg = MessageSegment.at(event.operator_id) + f"\n[禁言 {duration}s 指令触发成功]\n" + COMMAND_MAP[duration]
    try:
        await bot.send_group_msg(group_id=event.group_id, message=reply_msg)
    except Exception as e:
        logger.error(f"发送指令结果失败: {e}")
