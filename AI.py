import random
import math
import copy

class AIException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

def random_weight():
    return random.random()*2-1   #(-1,1)

def sigmod(z):
    if z>40:
        return 1.0
    if z<-709:
        return 0.0
    return 1/(1+math.exp(-z))

class Neuron(object):
    def __init__(self,count):
        self.weights=[]
        for i in range(count):
            self.weights.append(random_weight())

    def calculation(self,values):
        #ret=0
        if len(values)==len(self.weights):
            sum=0
            for i in range(len(values)):
                sum+=values[i]*self.weights[i]
            return sigmod(sum)
        elif len(values)==1 and len(self.weights)==0:
            return values[0]
        else:
            raise AIException('输入数据的个数和权值个数不相等')




class Layer(object):
    def __init__(self,n_count,pre_n_count=1):
        self.neurons=[]
        for i in range(n_count):
            self.neurons.append(Neuron(pre_n_count))


#[5,[4],1]
class NeuronNetwork(object):
    def __init__(self,input,hiddens,oupt):
        self.layer=[]
        pre_layer_n_count=0
        #初始化输入层
        input_layer=Layer(input,pre_layer_n_count)
        self.layers.append(input_layer)
        pre_layer_n_count=input
        #初始化隐藏层
        for hidden in hiddens:
            hidden_layer=Layer(hidden,pre_layer_n_count)
            self.layers.append(hidden_layer)
            pre_layer_n_count=hidden
        #初始化输出层
        oupput_layer=Layer(oupt,pre_layer_n_count)
        self.layers.append(oupput_layer)


    #data={"network":[5,4,1],'weight':[]}
    def get_network_data(self):
        # layers=[]
        # weights=[]
        data={'network':[],'weight':[]}
        for layer in self.layers:
            data['network'].append(len(layer.neurons))
            if layer==self.layers[0]:
                continue
            else:
                for neuron in layer.neurons:
                    data['weight'].extend(neuron.weights)
        return data



    def set_network_data(self,data):
        self.layers = []
        pre_layer_n_count = 0
        weight_index=0
        for i in range(len(data['network'])):
            layer=Layer(data['network'][i],pre_layer_n_count)
            for neuron in layer.neurons:
                for i in range(len(neuron.weights)):
                    neuron.weights[i]=data['weights'][weight_index]
                    weight_index+=1
            self.layers.append(layer)
            pre_layer_n_count=len(layer.neurons)



    def get_result(self,inputs):
        if len(inputs)==len(self.layers[0].neurons):
            raise AIException('输入的数据个数和输入层节点数不一致！！')
        input_values=[]
        output_values=[]
        for layer in self.layers:
            output_values=[]
            if layer==self.layers[0]:
                for i in range(len(inputs)):
                    value=layer.neurons[i].calculation(inputs[i])
                    output_values.append(value)
                #input_values=output_values
            else:
                for neuron in layer.neurons:
                    value=neuron.calculation(input_values)
                    output_values.append(value)
            input_values=output_values
        return output_values


class Genome(object):#表示一个个体
    def __init__(self,net_data,score):
        self.net_data=net_data
        self.score=score




class Generation(object):
    def __init__(self):
        self.genomes=[]

    def add_genome(self,genome):
        append_last=True
        for i in range(len(self.genomes)):
            if genome.score>self.genomes[i].score:
                self.genomes.insert(i,genome)
                append_last=False
                break
            if append_last:
                self.genomes.append(genome)

    def create_next_net_datas(self):
        next_net_datas=[]
            #精英原地复活进入下一代
        for i in range(round(population* elite_ratio)):
            next_net_datas.append(self.genomes[i].net_data)
        #石头里蹦出几个
        for i in range(round(population * newborn)):
            net=NeuronNetwork(network[0],network[1],network[2])
            next_net_datas.append(net.get_network_data())
        #遗传（交叉和变异）
        while True:
            father=self.genomes[0]
            mother=self.genomes[random.randint(1,len(self.genomes)-1)]

            child_net_data=self.breed(father,mother)
            next_net_datas.append(child_net_data)
            if len(next_net_datas)>=population:
                break
        return next_net_datas

    def breed(self,father,mother):
        child=copy.deepcopy(father)
        #交叉
        for i in range(len(child.net_data['weight'])):
            if random.random()<0.5:
                child.net_data['weight'][i]=mother.net_data['weight'][i]
        #变异
        for i in range(len(child.net_data['weight'])):
            if random.random()<mutation_ratio:
                child.net_data['weight'][i]=random_weight()
        return child.net_data



class GenerationManager(object):
    def __init__(self):
        self.generations=[]
    def first_generation(self):
        net_datas=[]
        for i in range(population):
            net=NeuronNetwork(network[0],network[1],network[2])
            net_datas.append(net.get_network_data())
        return net_datas

    def next_generation(self):
        if len(self.generations)>0:
            net_datas=self.generations[-1].create_next_net_datas()
            self.generations.append(Generation())
            return net_datas
        else:
            raise AIException('没有上一代种群用来生成下一代！！')

    def add_genome(self,genome):
        self.generations[-1].insert_genome(genome)




def ArtificialIntelligence(object):
    def __init__(self):
        self.manager=GenerationManager()

    def next_generation_networks(self):
        network=[]
        if len(self.manager.generations)==0:
            net_datas=self.manager.first_generation()
        else:
            net_datas=self.manager.next_generation()
        for net_data in net_datas:
            new_network=NeuronNetwork(network[0],network[1],network[2])
            new_network.set_network_data(net_data)
            network.append(new_network)
        if historic>0: #至少要保存一代，用于繁殖
            #当前种群世代列表超过保存值
            if len(self.manager.generations)>historic:
                #除去historic数量的记录，之前的全部删除，避免占用过多内存
                del self.manager.generations[0:len(self.manager.generations)-historic]
        return network

    def gather_score(self,t_network,t_course):
        self.manager.add_genome(Genome(t_network.get_network_data(),t_course))

network=[5,[4],1]
population=30     #种群个体的数量
elite_ratio=0.2   #遗传精英的比率
newborn=0.1       #每一代新生个体的比率
mutation_ratio=0.05  #产生突变的比率
historic=1           #最多保存多少代数据











