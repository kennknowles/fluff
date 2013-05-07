import fluff
from couchdbkit import Document
from unittest2 import TestCase
from datetime import date
from .mock_couch import MockCouch


class Base0(fluff.Calculator):
    @fluff.filter_by
    def base_0_filter(self):
        pass

    @fluff.date_emitter
    def base_0_emitter(self):
        pass


class Base1(Base0):
    @fluff.filter_by
    def base_1_filter(self):
        pass

    @fluff.date_emitter
    def base_1_emitter(self):
        pass


class Base2(Base0):
    @fluff.filter_by
    def base_2_filter(self):
        pass

    @fluff.date_emitter
    def base_2_emitter(self):
        pass


class Base3(Base1, Base2):
    @fluff.filter_by
    def base_3_filter(self):
        pass

    @fluff.date_emitter
    def base_3_emitter(self):
        pass


class Test(TestCase):
    def test_calculator_base_classes(self):
        # Base0
        self.assertEqual(Base0._fluff_emitters, set([
            'base_0_emitter',
        ]))
        self.assertEqual(Base0._fluff_filters, set([
            'base_0_filter',
        ]))

        # Base1
        self.assertEqual(Base1._fluff_emitters, set([
            'base_0_emitter',
            'base_1_emitter',
        ]))
        self.assertEqual(Base1._fluff_filters, set([
            'base_0_filter',
            'base_1_filter',
        ]))

        # Base2
        self.assertEqual(Base2._fluff_emitters, set([
            'base_0_emitter',
            'base_2_emitter',
        ]))
        self.assertEqual(Base2._fluff_filters, set([
            'base_0_filter',
            'base_2_filter',
        ]))

        # Base2
        self.assertEqual(Base3._fluff_emitters, set([
            'base_0_emitter',
            'base_1_emitter',
            'base_2_emitter',
            'base_3_emitter',
        ]))
        self.assertEqual(Base3._fluff_filters, set([
            'base_0_filter',
            'base_1_filter',
            'base_2_filter',
            'base_3_filter',
        ]))

    def test_indicator_calculation(self):
        pillow = MockIndicators.pillow()()
        pillow.processor({'changes': [], 'id': '123', 'seq': 1})
        indicator = mock_couch.mock_data.get("MockIndicators-123", None)
        print indicator
        self.assertIsNotNone(indicator)
        self.assertIn("visits_week", indicator)
        self.assertIn("all_visits", indicator["visits_week"])
        self.assertEqual("2012-09-23", indicator["visits_week"]["all_visits"][0])
        self.assertEqual("2012-09-24", indicator["visits_week"]["all_visits"][1])

    def test_indicator_diff(self):
        current = MockIndicators(domain="mock",
                                 owner_id="123",
                                 visits_week=dict(all_visits=[date(2012, 02, 23)],
                                                  null_emitter=[]))
        new = MockIndicators(domain="mock",
                             owner_id="123",
                             visits_week=dict(all_visits=[date(2012, 02, 24)],
                                              null_emitter=[None]))

        print new.diff(current)


mock_couch = MockCouch({"123": dict(actions=[dict(date="2012-09-23"), dict(date="2012-09-24")],
                                    get_id="123",
                                    domain="mock",
                                    owner_id="test_owner",
                                    emit_null=True)})


class MockDoc(Document):
    _db = mock_couch
    _doc_type = "Mock"


class VisitCalculator(fluff.Calculator):
    @fluff.date_emitter
    def all_visits(self, case):
        for action in case.actions:
            yield action['date']

    @fluff.null_emitter
    def null_emitter(self, case):
        if case.emit_null:
            yield None


class MockIndicators(fluff.IndicatorDocument):
    from datetime import timedelta

    _db = mock_couch
    document_class = MockDoc
    group_by = ('domain', 'owner_id')
    domains = ('test',)

    visits_week = VisitCalculator(window=timedelta(days=7))

