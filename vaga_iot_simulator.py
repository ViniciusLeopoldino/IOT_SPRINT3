import paho.mqtt.client as mqtt
import time
import json
import argparse

# As configurações do broker MQTT devem ser as mesmas em todos os arquivos
BROKER = 'broker.hivemq.com'
PORT = 1883

class VagaSimulator:
    """
    Esta classe simula o comportamento de um dispositivo IoT em uma vaga.
    Ele se conecta ao sistema MQTT e fica 'online', aguardando comandos
    ou realizando tarefas periódicas (se necessário).
    """
    def __init__(self, id_vaga):
        self.id_vaga = id_vaga
        # Tópico onde este simulador ouviria por comandos diretos (ex: piscar LED)
        self.topic_command = f"mottu/patio/vaga/{self.id_vaga}/command"
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """Callback chamado quando a conexão com o broker é estabelecida."""
        if rc == 0:
            print(f"[{self.id_vaga}] Simulador online. Conectado ao Broker MQTT.")
            # Se inscreve no tópico de comando para receber instruções do sistema
            client.subscribe(self.topic_command)
        else:
            print(f"[{self.id_vaga}] Falha na conexão, código: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback chamado quando uma mensagem chega no tópico de comando."""
        try:
            command = json.loads(msg.payload.decode())
            print(f"[{self.id_vaga}] Comando recebido: {command}")
            # Aqui poderíamos adicionar lógicas para atuar sobre o comando,
            # como "piscar_led", "soar_alarme", etc.
        except Exception as e:
            print(f"[{self.id_vaga}] Erro ao processar comando: {e}")

    def run(self):
        """Mantém o simulador rodando em um loop infinito."""
        try:
            # O loop principal apenas mantém o script vivo.
            # No mundo real, aqui estaria a leitura de sensores.
            while True:
                time.sleep(10) # A cada 10s, poderia, por exemplo, enviar um sinal de "heartbeat"
                # print(f"[{self.id_vaga}] Heartbeat.")

        except KeyboardInterrupt:
            print(f"[{self.id_vaga}] Simulador da vaga desligando.")
        finally:
            self.client.loop_stop()
            print(f"[{self.id_vaga}] Desconectado.")

# Ponto de entrada do script
if __name__ == "__main__":
    # Configura o script para aceitar argumentos da linha de comando (ex: --vaga A-01)
    parser = argparse.ArgumentParser(description="Simulador de Vaga IoT para Mottu Storage")
    parser.add_argument('--vaga', type=str, required=True, help='ID da vaga a ser simulada.')
    args = parser.parse_args()
    
    # Cria uma instância do simulador e o coloca para rodar
    simulator = VagaSimulator(id_vaga=args.vaga)
    simulator.run()