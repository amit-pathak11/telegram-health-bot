import random
from unittest import IsolatedAsyncioTestCase

from utils.helper import check_cooldown, enter_record, register_user, get_user


class TestRecord(IsolatedAsyncioTestCase):

    async def test_insert_record(self):
        r = random.randint(51512, 845151521)
        user_id = await get_user(r)
        self.assertEquals(None, user_id)

    async def test_if_record_exists(self):
        r = random.randint(51512, 845151521)
        await register_user(r, 'TestCase', 'Male', 18)
        user_id = await get_user(r)
        await enter_record(user_id, 'water', '2L')
        record = await check_cooldown(user_id, 'water')
        self.assertTrue(record[0])

    # Since this is a time dependent test we cannot execute this
    async def test_time_has_elapsed(self):
        pass
