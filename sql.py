import mysql.connector as mysql
import globals as g

class SQL():

    def __init__(self):
        config = {
            "host" : "127.0.0.1",
            "user" : "rasuser",
            "password" : "ras123",
            "database" : "rasdb"
        }
        self.connection = mysql.connect(**config)
        
###################### User Managing ######################

    def login(self,email,password):
        cursor = self.connection.cursor()

        cursor.execute('SELECT email FROM user WHERE user.email=%(email)s',{'email' : email})
        user = cursor.fetchone()
        if user:
            cursor.execute("SELECT password FROM user WHERE user.email=%(email)s AND user.password = %(password)s", {'email' : email, 'password' : password})
            if cursor.fetchone():
                return True
            else:
                print('Incorrect password!')
                return False
        else:
            print('No user with that email was found!')
            return False

        cursor.close()

    def register(self,**kw):
        cursor = self.connection.cursor()
        user_info = {
            'email' : kw['email'],
            'name' : kw['user'],
            'password' : kw['password'],
            'bday' : kw['bday'],
            'iban' : kw['iban'],
            'cc' : kw['cc']
        }
        cursor.execute("INSERT INTO user VALUES (%(email)s,%(name)s,%(password)s,%(iban)s,%(bday)s,%(cc)s)",user_info)
        moeda_info = {
            "tipo" : kw['tipo_moeda'],
            "montante" : kw['montante'],
            "user" : kw['email']
        }
        cursor.execute("INSERT INTO moeda (tipo,montante,user_email) VALUES (%(tipo)s,%(montante)s,%(user)s)",moeda_info)
        self.connection.commit()
        cursor.close()

    def checkBalance(self,user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
SELECT montante,tipo FROM moeda
WHERE user_email=%(email)s""", {'email':user_id})
        print('##### Current Balance #####')
        if db := cursor.fetchall():
            for coins in db:
                print(f'\t{coins[0]} {coins[1]}')
        print('###########################')
        cursor.close()

    def changePassword(self,new_password,user_id):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE user SET password = %(pass)s WHERE email = %(id)s", {'pass' : new_password, 'id' : user_id})
        self.connection.commit()
        cursor.close()

    def deposit(self,user_id,option,amount):
        cursor = self.connection.cursor()
        cursor.execute("SELECT EXISTS(SELECT * FROM moeda WHERE user_email=%(user)s AND tipo=%(tipo)s)",{"user":user_id,"tipo":option})
        if (r:=cursor.fetchone()[0]) == 1: 
            cursor.execute("UPDATE moeda SET montante = montante + %(amount)s WHERE user_email = %(id)s AND tipo=%(tipo)s", {"amount":amount,"id":user_id,"tipo":option} )
        else:
            cursor.execute("INSERT INTO moeda (tipo,montante,user_email) VALUES (%(tipo)s,%(amount)s,%(id)s)", {"amount":amount,"id":user_id,"tipo":option})
        self.connection.commit()
        cursor.close()

    def withdraw(self,user_id,option,amount):
        cursor = self.connection.cursor()
        cursor.execute("SELECT EXISTS(SELECT * FROM moeda WHERE user_email=%(user)s AND tipo=%(tipo)s)",{"user":user_id,"tipo":option})
        if (r:=cursor.fetchone()[0]) == 1: 
            cursor.execute("UPDATE moeda SET montante = montante - %(amount)s WHERE user_email = %(id)s AND tipo=%(tipo)s", {"amount":amount,"id":user_id,"tipo":option} )
        else:
            print('ERROR: Withdraw Not Possible.')
        self.connection.commit()

        cursor.close()


###################### Betting ###################### 

    def listAllBets(self, sport):
        cursor = self.connection.cursor()
        cursor.execute("SELECT odd_vitoriaCasa, equipaCasa, odd_empate, equipaVisitante, odd_vitoriaVisitante, id FROM jogo WHERE jogo.desporto=%(sport)s" , {'sport' : sport})
        if games := cursor.fetchall():
            print("Game ID --> TeamA OddWinA - OddTie - OddWinB TeamB")
            print("###################### Games to Bet ######################")
            for game in games:
                print(f"{game[5]} --> {game[1]} {game[0]} - {game[2]} - {game[4]} {game[3]} ")
            print("#########################################################")
        else:
            print('No games were found!')
        cursor.close()

    def betOnGameSimple(self,user_id,game_id,option,amount,odd_choice):
        cursor = self.connection.cursor()
        coin_info={
            'tipo' : option,
            'montante' : amount,
            'user' : user_id
        }
        bet_info = {
            'jogo' : game_id,
            'equipa' : odd_choice,
            'amount' : amount
        }  
        # Checking if gameId actually exists
        cursor.execute("SELECT * FROM jogo WHERE id = %(id)s",{'id' : game_id})
        if r:=cursor.fetchone():
            valor_odd = r[1+odd_choice]
            bet_info['valor_odd'] = valor_odd
            choice = int(input('1-Confirm\n2-Exit\nOption: '))
            if choice == 1:
                # Check if money is enough
                cursor.execute("SELECT montante FROM moeda WHERE user_email=%(user)s AND tipo=%(tipo)s",coin_info)
                if debit:=cursor.fetchone()[0] > amount:
                    # Commit bet
                    cursor.execute("INSERT INTO bet (jogo_id,valor,total_odd,equipaEscolhida) VALUES (%(jogo)s,%(amount)s,%(valor_odd)s,%(equipa)s)",bet_info)
                    self.connection.commit()
                    # Commit boletim
                    last_id = cursor.lastrowid
                    cursor.execute("INSERT INTO Boletim (user_email,bet_id) VALUES (%(user)s,%(bet)s)", {'user' : user_id, 'bet' : last_id})
                    self.connection.commit()
                else:
                    print('ERROR: Insufficient Funds')
            elif choice == 2:
                print('Bet Cancelled')
                return
            else:
                print('ERROR: Invalid Option')
        cursor.close()
    
    def betOnGameMultiple(self,user_id,games_betted):
        cursor = self.connection.cursor()
        # Fazer como na bet simples mas repetir para cada jogo que esteja no games_betted
        cursor.close()

    def seeBetHistory(self,email):
        cursor = self.connection.cursor()
        # Fecth all Boletins
        # For each boletim fetch all bets
        # Print bets
        # Tentar fazer paginação
        cursor.close()