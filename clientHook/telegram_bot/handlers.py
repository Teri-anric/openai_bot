from aiogram import Router, types


index_router = Router()


@index_router.message()
async def echo(m: types.Message):
    return m.answer("Hi")



