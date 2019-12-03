from apps.books.serializers import BookSerializer


class BorrowSerializer(object):
    @classmethod
    def serialize(cls, borrows, friends):
        friends_dict = {friend['external_id']: friend for friend in friends}
        return {
            "borrows": [{
                "id": borrow.pk,
                "friend": friends_dict[cls._get_friend_external_id(borrow)],
                "book": BookSerializer.serialize(borrow.book),
                "borrow_data": {
                    "take_date": borrow.take_date,
                    "planned_return_date": borrow.planned_return_date,
                    "real_return_date": borrow.real_return_date,
                }
            } for borrow in borrows]
        }

    @classmethod
    def _get_friend_external_id(cls, borrow):
        raise NotImplemented


class MyBorrowsSerializer(BorrowSerializer):
    @classmethod
    def _get_friend_external_id(cls, borrow):
        return borrow.book.account.vk_id


class FriendBorrowsSerializer(BorrowSerializer):
    @classmethod
    def _get_friend_external_id(cls, borrow):
        return borrow.borrower.vk_id
