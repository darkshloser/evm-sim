from pyethereum import transactions, blocks, processblock, utils
import serpent

# processblock.debug = 1


class TestNamecoin(object):

    SECRET_KEY = 'cow'
    STARTETH = 10**18
    GASPRICE = 10**12
    STARTGAS = 10000
    SCRIPT = 'examples/namecoin.se'

    @classmethod
    def setup_class(cls):
        cls.key = utils.sha3(cls.SECRET_KEY)
        cls.addr = utils.privtoaddr(cls.key)
        cls.code = serpent.compile(open(cls.SCRIPT).read())

    def load_contract(self, code, endowment=0):
        _tx = transactions.contract(nonce=self.nonce, gasprice=self.GASPRICE, startgas=self.STARTGAS,
                                    endowment=endowment, code=code).sign(self.key)
        result, contract = processblock.apply_tx(self.genesis, _tx)
        assert result

        self.nonce += 1
        return contract

    def setup_method(self, method):
        self.genesis = blocks.genesis({self.addr: self.STARTETH})
        self.nonce = 0
        self.contract = self.load_contract(self.code)

    def tx(self, to, value, data):
        _tx = transactions.Transaction(nonce=self.nonce, gasprice=self.GASPRICE, startgas=self.STARTGAS,
                                       to=to, value=value, data=serpent.encode_datalist(data)).sign(self.key)
        result, ans = processblock.apply_tx(self.genesis, _tx)
        assert result

        self.nonce += 1
        return serpent.decode_datalist(ans)

    def test_reservation(self):
        data = ['ethereum.bit', '54.200.236.204']
        ans = self.tx(self.contract, 0, data)

        assert ans == [1]
        assert self.genesis.get_storage(self.contract).to_dict() == {'ethereum.bit': '54.200.236.204'}

    def test_double_reservation(self):
        data = ['ethereum.bit', '127.0.0.1']
        ans = self.tx(self.contract, 0, data)
        assert ans == [1]

        data = ['ethereum.bit', '127.0.0.2']
        ans = self.tx(self.contract, 0, data)
        assert ans == [0]
        assert self.genesis.get_storage(self.contract).to_dict() == {'ethereum.bit': '127.0.0.1'}
