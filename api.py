from graphene.types import schema
import graphene
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_graphql import GraphQLView
from flask import render_template

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@hostname:portnumber/databasename'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Branches(db.Model):
    __tablename__ = 'branches'

    ifsc = db.Column(db.String(11), primary_key=True, nullable=False)
    bank_id = db.Column(db.BigInteger)
    branch = db.Column(db.String(74))
    address = db.Column(db.String(195))
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    state = db.Column(db.String(26))


class Banks(db.Model):
    __tablename___ = 'banks'

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.String(49))


class BanksObject(SQLAlchemyObjectType):
    class Meta:
        model = Banks
        interfaces = (graphene.relay.Node, )


class BranchesObject(SQLAlchemyObjectType):
    class Meta:
        model = Branches
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    get_branches = graphene.List(BranchesObject)
    get_branchesbyIfsc = graphene.List(BranchesObject, id=graphene.String())
    allbanks = SQLAlchemyConnectionField(BanksObject)
    allbranches = SQLAlchemyConnectionField(BranchesObject)

    def resolve_get_branches(parent, info, **args):
        return Branches.get_query(info).all()

    def resolve_get_branchesbyIfsc(parent, info, **args):
        branch_id = args.get('id')
        branches = BranchesObject.get_query(info)
        return branches.filter(Branches.ifsc.contains(branch_id)).all()

schema = graphene.Schema(query=Query)

@app.route("/")
def welcome():
    return render_template("index.html")


app.add_url_rule('/gql', view_func=GraphQLView.as_view('graphql',
                 schema=schema, graphiql=True,), endpoint = 'gql')

@app.route("/gql")
def show():
    "Just Added to Make Gql tempalte visible"
    print(f"<--None--->")

if __name__ == "__main__":
    app.run(debug=True)
